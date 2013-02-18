import sys
import time
import pika
from pika import exceptions
import json
import web
from time import time, sleep
from threading import Thread

import config
import geoip

"""
    Basic class to store and update information about each squid server.
"""
class SquidNode(object):
    def __init__(self, key, public_ip, private_ip, load, geo_data):
        self.key = key
        self.created = time()
        self.last_active = time()

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
        if geoip.check_geolitecity():
            geoip.download_geolitecity()

        try:
            rabbitmq_thread = Thread(target=self.rabbitmq, name='RabbitMQ')
            self.threads.append(rabbitmq_thread)

            webpy_thread = Thread(target=self.webpy, name='Webpy')
            self.threads.append(webpy_thread)

            update_thread = Thread(target=self.update, name="ShoalUpdate")
            self.threads.append(update_thread)

            for thread in self.threads:
                thread.start()

            while True:
                for thread in self.threads:
                    if not thread.is_alive():
                        print thread, " died."
                        sys.exit(1)

        except KeyboardInterrupt:
            self.webpy.stop()
            self.update.stop()
            self.rabbitmq.stop()
        except:
            self.webpy.stop()
            self.update.stop()
            self.rabbitmq.stop()

    def rabbitmq(self):
        self.rabbitmq = RabbitMQConsumer(self.shoal)
        self.rabbitmq.run()

    def webpy(self):
        self.webpy = WebpyServer(self.shoal)
        self.webpy.run()

    def update(self):
        self.update = ShoalUpdate(self.shoal)
        self.update.run()


"""
    ShoalUpdate is used for trimming inactive squids every set interval.
"""
class ShoalUpdate(object):

    def __init__(self, shoal):
        self.shoal = shoal
        self.interval = config.squid_cleanse_interval
        self.inactive = config.squid_inactive_time

    def run(self):
        while True:
            sleep(self.interval)
            self.update()

    def stop(self):
        sys.exit()

    def update(self):
        curr = time()
        for squid in self.shoal.values():
            if curr - squid.last_active > self.inactive:
                self.shoal.pop(squid.key)


"""
    Webpy webserver used to serve up active squid lists and restul API calls. For now we just use the development webpy server to serve requests.
"""
class WebpyServer(object):

    def __init__(self, shoal):
        web.shoal = shoal

    def run(self):
        urls = (
            '/', 'urls.index',
            '/nearest', 'urls.nearest',
        )
        self.app = web.application(urls, globals())
        self.app.internalerror = web.debugerror
        self.app.run()

    def stop(self):
        self.app.stop()

"""
    Basic RabbitMQ asynchronous consumer. Consumes messages from `QUEUE` takes the json in body, and put it into the dictionary `shoal`
    Messages received must be a json string with keys:
    {
      'public_ip': '142.11.52.1',
      'private_ip: '192.168.0.1',
      'load': '12324432',
    }
"""
class RabbitMQConsumer(object):

    def __init__(self, shoal):
        self.url = config.amqp_server_url
        self.queue = config.amqp_server_queue
        self.port = config.amqp_server_port
        self.shoal = shoal
        self.connection = None
        self.channel = None

    def run(self):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.url, self.port))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue)

            self.channel.basic_consume(self.on_message,queue=self.queue)

            self.channel.start_consuming()
        except exceptions.AMQPConnectionError as e:
            print 'Could not connect to AMQP Server.', e
            sys.exit(1)

    def on_message(self, ch, method_frame, properties, body):
        try:
            data = json.loads(body)

            key = data['uuid']
            public_ip = data['public_ip']
            private_ip = data['private_ip']
            load = data['load']
            geo_data = geoip.get_geolocation(public_ip)

            if key in self.shoal:
                self.shoal[key].update(public_ip, private_ip, load, geo_data)
            else:
                new_squid = SquidNode(key, public_ip, private_ip, load, geo_data)
                self.shoal[key] = new_squid

        except KeyError as e:
            print "Message received was not the proper format (missing:{}), discarding...".format(e)
        finally:
            self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def stop(self):
        self.channel.stop_consuming()
        self.connection.close()


"""
    Main function to run Shoal.
"""
def main():
    app = Application()

if __name__ == '__main__':
    main()
