import sys
import web
import json
import logging
import argparse

import pika

from time import time, sleep
from threading import Thread

import config
import geoip
import urls

logging.basicConfig()
logging.getLogger('shoal').setLevel(logging.WARNING)

"""
    Basic class to store and update information about each squid server.
"""
class SquidNode(object):
    def __init__(self, key, public_ip, private_ip, load, geo_data, last_active=time()):
        self.key = key
        self.created = time()
        self.last_active = last_active

        self.public_ip = public_ip
        self.private_ip = private_ip
        self.load = load
        self.geo_data = geo_data

    def update(self, public_ip, private_ip, load, geo_data):
        self.last_active = time()

        self.public_ip = public_ip
        self.private_ip = private_ip
        self.load = load
        self.geo_data = geo_data

"""
    Main application that will delegate threads.
"""
class Application(object):

    def __init__(self):
        # setup configuration settings.
        config.setup()
        self.shoal = {}
        self.threads = []

        # check if geolitecity database needs updating
        if geoip.check_geolitecity_need_update():
            geoip.download_geolitecity()

        rabbitmq_thread = Thread(target=self.rabbitmq, name='RabbitMQ')
        rabbitmq_thread.daemon = True
        self.threads.append(rabbitmq_thread)

        webpy_thread = Thread(target=self.webpy, name='Webpy')
        webpy_thread.daemon = True
        self.threads.append(webpy_thread)

        update_thread = Thread(target=self.update, name="ShoalUpdate")
        update_thread.daemon = True
        self.threads.append(update_thread)

        for thread in self.threads:
            thread.start()

        try:
            while True:
                for thread in self.threads:
                    if not thread.is_alive():
                        logging.error('{} died.'.format(thread))
                        self.stop()
        except KeyboardInterrupt:
            self.stop()

    def rabbitmq(self):
        self.rabbitmq = RabbitMQConsumer(self.shoal)
        self.rabbitmq.run()

    def webpy(self):
        self.webpy = WebpyServer(self.shoal)
        self.webpy.run()

    def update(self):
        self.update = ShoalUpdate(self.shoal)
        self.update.run()

    def stop(self):
        try:
            self.webpy.stop()
            self.rabbitmq.stop()
            self.update.stop()
        except Exception as e:
            logging.error(e)
        finally:
            # give them time to properly exit.
            sleep(2)
            sys.exit()

"""
    ShoalUpdate is used for trimming inactive squids every set interval.
"""
class ShoalUpdate(object):

    def __init__(self, shoal):
        self.shoal = shoal
        self.interval = config.squid_cleanse_interval
        self.inactive = config.squid_inactive_time
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            sleep(self.interval)
            self.update()

    def update(self):
        curr = time()
        for squid in self.shoal.values():
            if curr - squid.last_active > self.inactive:
                self.shoal.pop(squid.key)

    def stop(self):
        self.running = False

"""
    Webpy webserver used to serve up active squid lists and API calls. For now we just use the development webpy server to serve requests.
"""
class WebpyServer(object):

    def __init__(self, shoal):
        web.shoal = shoal
        web.config.debug = False
        self.app = None
        self.urls = (
            '/nearest', 'urls.nearest',
            '/external', 'urls.external_ip',
            '/(.*)', 'urls.index',
        )
    def run(self):
        try:
            self.app = web.application(self.urls, globals())
            self.app.run()
        except Exception as e:
            logging.error("Could not start webpy server.\n{}".format(e))
            sys.exit(1)

    def stop(self):
        self.app.stop()

"""
    Basic RabbitMQ blocking consumer. Consumes messages from `config.amqp_server_queue` takes the json in body, and put it into the dictionary `shoal`
    Messages received must be a json string with keys or it will be discarded.
    {
      'uuid': '1231232',
      'public_ip': '142.11.52.1',
      'private_ip: '192.168.0.1',
      'load': '12324432',
      'timestamp':'2121231313',
    }
"""
class RabbitMQConsumer(object):

    def __init__(self, shoal):
        self.url = config.amqp_server_url
        self.queue = config.amqp_server_queue
        self.port = config.amqp_server_port
        self.exchange = config.amqp_exchange
        self.exchange_type = config.amqp_exchange_type
        self.routing_key = '#'
        self.shoal = shoal
        self.connection = None
        self.channel = None

    def run(self):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.url, self.port))

            self.channel = self.connection.channel()

            self.channel.exchange_declare(exchange=self.exchange,
                                     type=self.exchange_type)

            self.channel.queue_declare(queue=self.queue)

            self.channel.queue_bind(exchange=self.exchange, queue=self.queue,
                               routing_key=self.routing_key)

            self.channel.basic_consume(self.on_message, self.queue)

            self.channel.start_consuming()

        except Exception as e:
            logging.error('Could not connected to AMQP Server. Error: {}'.format(e))

    def on_message(self, unused_channel, method_frame, properties, body):
        try:
            print method_frame
            print properties
            print body
            squid_inactive_time = config.squid_inactive_time
            curr = time()
            data = json.loads(body)

            key = data['uuid']
            external_ip = ['external_ip']
            public_ip = data['public_ip']
            private_ip = data['private_ip']
            load = data['load']
            geo_data = geoip.get_geolocation(external_ip)
            last_active = data['timestamp']

            if key in self.shoal:
                self.shoal[key].update(public_ip, private_ip, load, geo_data)
            elif curr - last_active < squid_inactive_time:
                new_squid = SquidNode(key, public_ip, private_ip, load, geo_data, last_active)
                self.shoal[key] = new_squid

        except KeyError as e:
            logging.error("Message received was not the proper format (missing:{}), discarding...\nmethod_frame:{}\nproperties:{}\nbody:{}\n".format(e,method_frame,properties,body))

        finally:
            self.channel.basic_ack(method_frame.delivery_tag)

    def stop(self):
        self.channel.stop_consuming()


def main():
    app = Application()

if __name__ == '__main__':
    main()
