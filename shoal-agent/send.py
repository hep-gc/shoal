#!/usr/bin/env python

# Author: Mike Chester <mchester@uvic.ca>
# Copyright (C) 2013 University of Victoria
# You may distribute under the terms of either the GNU General Public
# License or the Apache v2 License.

import sys
import json
import pika
import time
import netifaces
import uuid
from os import fork, chdir, setsid, umask

# RabbitMQ Server
HOST = 'localhost'
PORT = 5672
QUEUE = 'squiddata'
EXCHANGE = 'shoal'
EXCHANGE_TYPE = 'topic'
ROUTING_KEY = 'elephant.info'

# Time interval to send data
INTERVAL = 30
# Unique ID for this squid.
ID = str(uuid.uuid1())
IFACE = 'eth0'

def amqp_send(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                    HOST, PORT))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, type=EXCHANGE_TYPE)
    channel.basic_publish(exchange=EXCHANGE,
                          routing_key=ROUTING_KEY,
                          body=data)
    connection.close()

def get_load_data():
    received_file = '/sys/class/net/%s/statistics/rx_bytes' % IFACE
    transmitted_file = '/sys/class/net/%s/statistics/tx_bytes' % IFACE
    with open(received_file) as rx:
        with open(transmitted_file) as tx:
            rx1 = int(rx.read())
            tx1 = int(tx.read())
            rx.close()
            tx.close()
    time.sleep(1)
    with open(received_file) as rx:
        with open(transmitted_file) as tx:
            rx2 = int(rx.read())
            tx2 = int(tx.read())
            rx.close()
            tx.close()

    rx_rate = (rx2 - rx1) / 1024
    tx_rate = (tx2 - tx1) / 1024
    return {'in':rx_rate, 'out':tx_rate}

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
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            sys.exit()

if __name__ == '__main__':
    try:
        pid = fork()
        if pid > 0:
            exit(0)
    except OSError, e:
        exit(1)
    chdir("/")
    setsid()
    umask(0)
    try:
        pid = fork()
        if pid > 0:
            exit(0)
    except OSError, e:
        exit(1)
    main()
