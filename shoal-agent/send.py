#!/usr/bin/env python
import sys
import json
import pika
import subprocess
import time
import netifaces
import uuid

# RabbitMQ Server
BROKER = 'elephant105.heprc.uvic.ca'
# RabbitMQ Queue message will be sent to
QUEUE = 'squiddata'
# Time interval to send data
INTERVAL = 30
# Unique ID for this squid.
ID = str(uuid.uuid1())

"""
    T_Collector script (or any script) that will output metric data
    to keep it consistant with T_Collector used with phantom output should be of the format:
    (name of your sensor) (current time) (value)
    eg. name.of.your.sensor 123412312 1000
"""
TC_SCRIPT = '/home/mchester/shoal/shoal-agent/netspeed'
NIC = 'eth0'

# Sensors to get byte rate in and out, using above script.
BYTE_RATE_IN = ['proc.net.bytes.inrate',NIC]
BYTE_RATE_OUT = ['proc.net.bytes.outrate',NIC]

def amqp_send(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                    BROKER, 5672))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE)

    channel.basic_publish(exchange='',
                          routing_key=QUEUE,
                          body=data)
    connection.close()

def get_load_data():
    cmd = [TC_SCRIPT,NIC]
    try:
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    except Exception as e:
        print "Could not get load information.",e
        sys.exit(1)
    p.wait()
    out,err = p.communicate()
    out = out.split('\n')

    data = {}
    for line in out:
        if all(s in line for s in BYTE_RATE_IN):
            data['in'] = line.split()[2]
        if all(s in line for s in BYTE_RATE_OUT):
            data['out'] = line.split()[2]
    return data

def get_ip_addresses():
    for interface in netifaces.interfaces():
        try:
            for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                if 'lo' in interface:
                    private = link['addr']
                else:
                    public = link['addr']
        except:
            continue
    return public, private

def main():
    while True:
        public, private = get_ip_addresses()
        data = {
                'uuid': ID,
                'public_ip': public,
                'private_ip': private,
                'load': get_load_data(),
               }

        json_str = json.dumps(data)

        amqp_send(json_str)

        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
