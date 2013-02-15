#!/usr/bin/env python
import json
import pika
import socket
import subprocess
import time

# RabbitMQ Server
BROKER = 'elephant106.heprc.uvic.ca'
# RabbitMQ Queue message will be sent to
QUEUE = 'squiddata'
# Time interval to send data
INTERVAL = 30
"""
    T_Collector script (or any script) that will output metric data
    to keep it consistant with T_Collector used with phantom output should be of the format:
    (name of your sensor) (current time) (value)
    eg. name.of.your.sensor 123412312 1000
"""
TC_SCRIPT = '/home/mchester/rabbitmq_helloworld/ifstat.py'

"""
    Can ignore if using your own script (and change the get_load_data function).
    If using T_Collector collectors, the sensor name is not unique and could contain other parametres
    example output:
                        proc.net.bytes 1360969715 1793351820 iface=eth0 direction=in
                        proc.net.bytes 1360969715 1016418000 iface=eth0 direction=out
                        proc.net.bytes 1360969715 1793351820 iface=eth1 direction=in
                        proc.net.bytes 1360969715 1016418000 iface=eth1 direction=out

    to get `proc.net.bytes 1360969715 1793351820 iface=eth1 direction=in`
    add ['proc.net.bytes','direction=in','eth1'] to LOAD_SENSOR value.
"""
LOAD_SENSOR = ['proc.net.bytes','direction=out','eth0']

def amqp_send(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                    BROKER, 5672))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE)

    channel.basic_publish(exchange='',
                          routing_key=QUEUE,
                          body=data)
    print " [x] Sent ",data
    connection.close()

def get_load_data():
    try:
        p = subprocess.Popen(TC_SCRIPT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    except Exception as e:
        print "Could not get load information.",e
        sys.exit(1)
    p.wait()
    out,err = p.communicate()
    out = out.split('\n')
    for line in out:
        if all(s in line for s in LOAD_SENSOR):
            return line.split()[2]
def main():
    while True:
        data = {
                'public_ip': socket.gethostbyname(socket.gethostname()),
                'private_ip': '',
                'load': get_load_data(),
               }

        json_str = json.dumps(data)

        amqp_send(json_str)

        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
