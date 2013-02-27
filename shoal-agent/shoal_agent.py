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
import config
import logging
from os import fork, chdir, setsid, umask

# Time interval to send data
INTERVAL = config.interval

# Unique ID for this squid.
ID = str(uuid.uuid1())
logging.basicConfig()
log = logging.getLogger('shoal_agent')

def amqp_send(data):
    exchange = config.amqp_exchange
    exchange_type = config.amqp_exchange_type
    host = config.amqp_server_url
    port = config.amqp_server_port
    cloud = config.cloud
    routing_key = cloud + '.info'

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, type=exchange_type)
        channel.basic_publish(exchange=exchange,
                              routing_key=routing_key,
                              body=data)
        connection.close()
    except Exception as e:
        log.error('Could not connect to AMQP Server. Error: %s' % e)
        sys.exit(1)
    except:
        pass

def get_load_data():
    with open('/sys/class/net/eth0/statistics/tx_bytes') as tx:
        tx1 = int(tx.read())
        tx.close()

    time.sleep(1)

    with open('/sys/class/net/eth0/statistics/tx_bytes') as tx:
        tx2 = int(tx.read())
        tx.close()

    tx_rate = (tx2 - tx1) / 1024

    return tx_rate

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
    config.setup()
    set_logger()
    while True:
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

def set_logger():
    log_file = config.log_file
    log_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)s] - %(message)s'
    log = logging.getLogger('shoal_agent')
    hdlr = logging.FileHandler(log_file)
    formatter = logging.Formatter(log_format)

    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.WARNING)

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
