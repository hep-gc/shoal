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
import socket
import config
import logging
import urllib2

# Time interval to send data
INTERVAL = config.interval

logging.basicConfig()
log = logging.getLogger('shoal_agent')
private_address = ('10.','172.','192.')

def get_external_ip():
    url = config.external_ip_service
    try:
        f = urllib2.urlopen(url)
    except urllib2.URLError as e:
        logging.error("Unable to open '%s', is the shoal service running?" % url)
        return None
    data = json.loads(f.read())
    return data['external_ip']

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
    public = private = None
    for interface in netifaces.interfaces():
        try:
            for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                if link['addr'].startswith(private_address):
                    private = link['addr']
                elif not link['addr'].startswith('127.'):
                    public = link['addr']
        except Exception as e:
            continue
    return public, private

def main():
    config.setup()
    set_logger()

    # make a UUID based on the, host ID and current time
    id = str(uuid.uuid1())
    hostname = socket.gethostname()

    data = {
            'uuid': id,
            'hostname': hostname,
           }

    public_ip, private_ip = get_ip_addresses()
    external_ip = get_external_ip()

    if private_ip:
        data['private_ip'] = private_ip

    if public_ip:
        data['public_ip'] = public_ip
    else:
        data['external_ip'] = external_ip

    while True:
        # if shoal was down when service started, external ip will be none
        # this could also occur if there was no internet connectivity when shoal_agent was started.
        # we need a public_ip or external_ip to generate the geolocation data, this will make sure atleast one is set.
        if not (public_ip or external_ip):
            external_ip = get_external_ip()
            data['external_ip'] = external_ip


        data['timestamp'] = time.time()
        data['load'] = get_load_data()

        if 'public_ip' in data or 'external_ip' in data:
            amqp_send(json.dumps(data))

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
    main()
