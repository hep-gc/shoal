#!/usr/bin/env python

# Author: Mike Chester <mchester@uvic.ca>
# Copyright (C) 2013 University of Victoria
# You may distribute under the terms of either the GNU General Public
# License or the Apache v2 License.

import sys
import json
import pika
import subprocess
import time
import netifaces
import uuid
import os

# RabbitMQ Server
HOST = 'localhost'
PORT = 5672
EXCHANGE = 'shoal'
EXCHANGE_TYPE = 'topic'
ROUTING_KEY = 'elephant.info'
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
TC_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'netspeed.sh')
NIC = 'eth0'

# Sensors to get byte rate in and out, using above script.
BYTE_RATE_IN = ['proc.net.bytes.inrate',NIC]
BYTE_RATE_OUT = ['proc.net.bytes.outrate',NIC]

def amqp_send(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                    HOST, PORT))
    channel = connection.channel()

    channel.exchange_declare(EXCHANGE, EXCHANGE_TYPE)

    channel.basic_publish(exchange=EXCHANGE,
                          routing_key=ROUTING_KEY,
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
        try:
            public, private = get_ip_addresses()
            data = {
                    'uuid': ID,
                    'public_ip': public,
                    'private_ip': private,
                    'load': get_load_data(),
                    'timestamp': time.time(),
                   }

            json_str = json.dumps(data)

            amqp_send(json_str)
            time.sleep(INTERVAL
        except KeyboardInterrupt:
            sys.exit()

if __name__ == '__main__':
    main()
