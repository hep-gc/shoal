import sys
import time
import pika
import json
import web
from threading import Thread
import os.path
import time
import subprocess
from webpy import geoip

DB_PATH = '/home/mchester/shoal/shoal/GeoLiteCity.dat'
DB_URL = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'

"""
    Basic class to store information about each squid server.
"""
class SquidNode(object):
    def __init__(self,key, public_ip, private_ip, load, geo_data):
        self.key = key
        self.created = time.time()
        self.last_active = time.time()

        self.public_ip = public_ip
        self.private_ip = private_ip
        self.load = load
        self.geo_data = geo_data

    def update(self, public_ip, private_ip, load, geo_data):
        self.last_active = time.time()

        self.public_ip =public_ip
        self.private_ip = private_ip
        self.load = load
        self.geo_data = geo_data

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
        self.update_database = self.check_database()

    def run(self):
        if self.update_database:
            try:
                download_database()
            except Exception as e:
                print "Could not update GeoLiteCity database."
            finally:
                pass
        while True:
            time.sleep(int(self.interval/2))
            self.process_messages()
            time.sleep(int(self.interval/2))

    def stop(self):
        sys.exit()

    def process_messages(self):
        curr = time.time()
        for squid in self.shoal.values():
            if curr - squid.last_active > 180:
                self.shoal.pop(squid.key)

    def check_database(self):
        curr = time.time()
        if os.path.exists(DB_PATH):
            if os.path.getmtime(DB_PATH) - curr > 2592000:
                return True
            else:
                return False
        else:
            return True


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
    Messages received must be a json string with keys:
    {
      'public_ip': '142.11.52.1',
      'private_ip: '192.168.0.1',
      'load': '12324432',
    }
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
        try:
            data = json.loads(body)

            key = data['public_ip']
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

def download_database(self):
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

"""
    Main function to run Shoal.
"""
def main():
    app = Application()

if __name__ == '__main__':
    main()
