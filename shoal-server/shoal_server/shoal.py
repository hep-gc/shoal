#!/usr/bin/env python
import sys
import os
import web
import json
import urllib
import logging
import pika
import socket
import uuid
from time import time, sleep
from threading import Thread

from shoal_server import config
from shoal_server import utilities

"""
    Basic class to store and update information about each squid server.
"""
class SquidNode(object):

    def __init__(self, key, hostname, squid_port, public_ip, private_ip, external_ip, load, geo_data, last_active=time()):
        self.key = key
        self.created = time()
        self.last_active = last_active
        self.hostname = hostname
        self.squid_port = squid_port
        self.public_ip = public_ip
        self.private_ip = private_ip
        self.external_ip = external_ip
        self.geo_data = geo_data
        self.load = load

    def update(self, load):
        self.last_active = time()
        self.load = load

    def jsonify(self):
        return dict({
                  "created": self.created,
                  "last_active": self.last_active,
                  "hostname": self.hostname,
                  "squid_port": self.squid_port,
                  "public_ip": self.public_ip,
                  "private_ip": self.private_ip,
                  "external_ip": self.external_ip,
                  "geo_data": self.geo_data,
                  "load": self.load,
                },
               )

"""
    Main application that will monitor RabbitMQ and ShoalUpdate threads.
"""
class ThreadMonitor(Thread):

    def __init__(self, shoal):
        # check if geolitecity database needs updating
        if utilities.check_geolitecity_need_update():
            utilities.download_geolitecity()

        Thread.__init__(self)

        self.shoal = shoal
        self.threads = []

        rabbitmq_thread = RabbitMQConsumer(self.shoal)
        rabbitmq_thread.daemon = True
        self.threads.append(rabbitmq_thread)

        update_thread = ShoalUpdate(self.shoal)
        update_thread.daemon = True
        self.threads.append(update_thread)

    def run(self):
        for thread in self.threads:
            print "starting", thread
            thread.start()
        while True:
            for thread in self.threads:
                if not thread.is_alive():
                    logging.error('{0} died. Stopping application...'.format(thread))
                    sys.exit(1)
            sleep(1)

    def stop(self):
        print "\nShutting down Shoal-Server... Please wait."
        try:
            self.rabbitmq.stop()
            self.update.stop()
        except Exception as e:
            logging.error(e)
            sys.exit(1)
        finally:
            sleep(2)
        sys.exit()

"""
    ShoalUpdate is used for trimming inactive squids every set interval.
"""
class ShoalUpdate(Thread):

    INTERVAL = config.squid_cleanse_interval
    INACTIVE = config.squid_inactive_time

    def __init__(self, shoal):
        Thread.__init__(self)
        self.shoal = shoal
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            sleep(self.INTERVAL)
            self.update()

    def update(self):
        curr = time()
        for squid in self.shoal.values():
            if curr - squid.last_active > self.INACTIVE:
                self.shoal.pop(squid.key)

    def stop(self):
        self.running = False

"""
    Webpy webserver used to serve up active squid lists and API calls. Can run as either the development server or under mod_wsgi.
"""
class WebpyServer(Thread):

    def __init__(self, shoal):
        Thread.__init__(self)
        web.shoal = shoal
        web.config.debug = False
        self.app = None
        self.urls = (
            '/nearest/?(\d+)?/?', 'shoal_server.view.nearest',
            '/wpad.dat', 'shoal_server.view.wpad',
            '/(\d+)?/?', 'shoal_server.view.index',
        )
    def run(self):
        try:
            self.app = web.application(self.urls, globals())
            self.app.run()
        except Exception as e:
            logging.error("Could not start webpy server.\n{0}".format(e))
            sys.exit(1)

    def wsgi(self):
        return web.application(self.urls, globals()).wsgifunc()

    def stop(self):
        self.app.stop()

"""
    Basic RabbitMQ async consumer. Consumes messages from a unique queue that is declared when Shoal server first starts.
    The consumer takes the json in message body, and tracks it in the dictionary `shoal`
"""
class RabbitMQConsumer(Thread):

    QUEUE = socket.gethostname() + "-" + uuid.uuid1().hex
    EXCHANGE = config.amqp_exchange
    EXCHANGE_TYPE = config.amqp_exchange_type
    ROUTING_KEY = '#'
    INACTIVE = config.squid_inactive_time

    def __init__(self, shoal):
        Thread.__init__(self)
        self.host = "{0}/{1}".format(config.amqp_server_url, urllib.quote_plus(config.amqp_virtual_host))
        self.shoal = shoal
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None

    def connect(self):
 	sslOptions = {}
        try: 
          if config.use_ssl:
            sslOptions["ca_certs"] = config.amqp_ca_cert
            sslOptions["certfile"] = config.amqp_client_cert
            sslOptions["keyfile"]  = config.amqp_client_key
	except Exception as e:
	  logging.error("Could not read SSL files")
	  logging.error(e)
        try:
            return pika.SelectConnection(pika.ConnectionParameters(
						host=config.amqp_server_url,
                                                port=config.amqp_port,
                                                ssl=config.use_ssl,
                                                ssl_options = sslOptions
					     ),
                                             self.on_connection_open,
                                             stop_ioloop_on_close=False)
        except pika.exceptions.AMQPConnectionError as e:
            logging.error("Could not connect to AMQP Server. Retrying in 30 seconds...")
            sleep(30)
            self.run()

    def close_connection(self):
        self._connection.close()

    def add_on_connection_close_callback(self):
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logging.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def on_connection_open(self, unused_connection):
        self.add_on_connection_close_callback()
        self.open_channel()

    def reconnect(self):
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()
        if not self._closing:
            # Create a new connection
            self._connection = self.connect()
            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def add_on_channel_close_callback(self):
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        logging.warning('Channel was closed: (%s) %s', reply_code, reply_text)
        self._connection.close()

    def on_channel_open(self, channel):
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def setup_exchange(self, exchange_name):
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        self._channel.queue_declare(self.on_queue_declareok, queue_name, auto_delete=True)

    def on_queue_declareok(self, method_frame):
        self._channel.queue_bind(self.on_bindok, self.QUEUE,
                                 self.EXCHANGE, self.ROUTING_KEY)

    def add_on_cancel_callback(self):
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        self._channel.basic_ack(delivery_tag)

    def on_cancelok(self, unused_frame):
        self.close_channel()

    def stop_consuming(self):
        if self._channel:
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def start_consuming(self):
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.QUEUE)

    def on_bindok(self, unused_frame):
        self.start_consuming()

    def close_channel(self):
        self._channel.close()

    def open_channel(self):
        self._connection.channel(on_open_callback=self.on_channel_open)

    def run(self):
        try:
            self._connection = self.connect()
        except Exception as e:
            logging.error("Unable to connect ot RabbitMQ Server. {0}".format(e))
            sys.exit(1)
        self._connection.ioloop.start()

    def stop(self):
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        external_ip = public_ip = private_ip = None
        curr = time()

        try:
            data = json.loads(body)
        except ValueError as e:
            logging.error("Message body could not be decoded. Message: {1}".format(body))
            self.acknowledge_message(basic_deliver.delivery_tag)
            return
        try:
            key = data['uuid']
            hostname = data['hostname']
            time_sent = data['timestamp']
            load = data['load']
            squid_port = data['squid_port']
        except KeyError as e:
            logging.error("Message received was not the proper format (missing:{0}), discarding...".format(e))
            self.acknowledge_message(basic_deliver.delivery_tag)
            return
        try:
            external_ip = data['external_ip']
        except KeyError:
            pass
        try:
            public_ip = data['public_ip']
        except KeyError:
            pass
        try:
            private_ip = data['private_ip']
        except KeyError:
            pass
        if key in self.shoal:
            self.shoal[key].update(load)
        elif (curr - time_sent < self.INACTIVE) and (public_ip or private_ip):
            geo_data = utilities.get_geolocation(public_ip)
            if not geo_data:
                geo_data = utilities.get_geolocation(external_ip)
            if not geo_data:
                logging.error("Unable to generate geo location data, discarding message")
            else:
                new_squid = SquidNode(key, hostname, squid_port, public_ip, private_ip, external_ip, load, geo_data, time_sent)
                self.shoal[key] = new_squid

        self.acknowledge_message(basic_deliver.delivery_tag)
