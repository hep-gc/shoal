import sys
import time
import pika
import json
import web
from threading import Thread
import os.path
import time
import subprocess

DB_PATH = '/home/mchester/shoal/shoal/GeoLiteCity.dat'
DB_URL = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'

"""
    Basic class to store information about each squid server.
"""
class SquidNode(object):
    def __init__(self,ip):
        self.key = ip
        self.created = time.time()

        self.last_active = time.time()
        self.rabbitmq = {}
        self.data = {}

    def update(self, rabbitmq, data):
        self.last_active = time.time()
        self.rabbitmq = rabbitmq
        self.data = data

"""
    Main application that will delegate threads.
"""
class Application(object):
    def __init__(self):
        self.shoal = {}
        self.threads = []
        try:
            rabbitmq_thread = Thread(target=self.rabbitmq, name='RabbitMQ')
            self.threads.append(rabbitmq_thread)

            webpy_thread = Thread(target=self.webpy, name='Webpy')
            self.threads.append(webpy_thread)

            middleware = Thread(target=self.middleware, name="ShoalMiddleware")
            self.threads.append(middleware)

            for thread in self.threads:
                thread.start()

            while True:
                for thread in self.threads:
                    if not thread.is_alive():
                        print thread, " died."
                        sys.exit(1)

        except KeyboardInterrupt:
            self.rabbitmq.stop()
            self.webpy.stop()
            self.update.stop()
        except:
            self.rabbitmq.stop()
            self.webpy.stop()
            self.update.stop()

    def rabbitmq(self):
        self.rabbitmq = RabbitMQConsumer('elephant106.heprc.uvic.ca', self.shoal)
        self.rabbitmq.run()

    def webpy(self):
        self.webpy = WebServer(self.shoal)
        self.webpy.run()

    def middleware(self):
        self.update = ShoalMiddleware(10,self.shoal)
        self.update.run()

class ShoalMiddleware():
    def __init__(self, interval, shoal):
        self.shoal = shoal
        self.interval = interval

    def run(self):
        curr = time.time()
        if os.path.exists(DB_PATH):
            if os.path.getmtime(DB_PATH) - curr > 2592000:
                self.download_db()
        else:
            self.download_db()
        while True:
            time.sleep(int(self.interval/2))
            self.process_messages()
            time.sleep(int(self.interval/2))

    def process_messages(self):
        curr = time.time()
        for squid in self.shoal.values():
            print squid
            if curr - squid.last_active > 180:
                self.shoal.pop(squid.key)

    def download_db(self):
        cmd = ['wget',DB_URL]
        ungz = ['gunzip','{0}.gz'.format(DB_PATH)]
        try:
            dl = subprocess.Popen(cmd)
            dl.wait()
            time.sleep(2)
            gz = subprocess.Popen(ungz)
            gz.wait()
        except Exception as e:
            print "Could not download the database. - {0}".format(e)
            sys.exit(1)

    def stop(self):
        sys.exit()

"""
    Webpy webserver used to serve up active squid lists and restul API calls. For now we just use the development webpy server to serve requests.
"""
class WebServer(object):

    def __init__(self, shoal):
        web.shoal = shoal

    def run(self):
        urls = (
            '/', 'webpy.urls.index',
            '/nearest', 'webpy.urls.nearest',
        )
        self.app = web.application(urls,globals())
        self.app.internalerror = web.debugerror
        self.app.run()

    def stop(self):
        self.app.stop()

"""
    Basic RabbitMQ asynchronous consumer. Consumes messages from `QUEUE` takes the json in body, and put it into the dictionary `shoal`
"""
class RabbitMQConsumer(object):
    def __init__(self, amqp_url, shoal):
        self.url = amqp_url
        self.queue = 'squiddata'
        self.shoal = shoal
        self.connection = None
        self.channel = None

    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.url))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

        self.channel.basic_consume(self.on_message,queue=self.queue)

        self.channel.start_consuming()

    def on_message(self, ch, method_frame, properties, body):
        data = json.loads(body)
        rabbitmq = {'method_frame':method_frame, 'properties':properties,}
        key = data['public_ip']

        if key in self.shoal:
            self.shoal[key].update(rabbitmq,data)
        else:
            new_squid = SquidNode(key)
            new_squid.rabbitmq = rabbitmq
            new_squid.data = data
            self.shoal[key] = new_squid

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
