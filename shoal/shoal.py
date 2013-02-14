import sys
import time
import pika
import json
import web
from threading import Thread

"""
    Main application that will delegate threads.
"""
class Application(object):
    def __init__(self):
        self.shoal = []
        self.threads = []
        try:
            rabbitmq_thread = Thread(target=self.rabbitmq, name='RabbitMQ')
            self.threads.append(rabbitmq_thread)

            webpy_thread = Thread(target=self.webpy, name='Webpy')
            self.threads.append(webpy_thread)

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
        except:
            self.rabbitmq.stop()
            self.webpy.stop()

    def rabbitmq(self):
        self.rabbitmq = RabbitMQConsumer('amqp://guest:guest@elephant106.heprc.uvic.ca:5672/%2F', self.shoal)
        self.rabbitmq.run()

    def webpy(self):
        self.webpy = WebServer(self.shoal)
        self.webpy.run()

"""
    Basic class to store information about each squid server.
"""
class SquidNode(object):

    def __init__(self,ip):
        self.created = time.time()
        self.last_active = time.time()
        self.ip = ip
        self.rabbitmq = {}
        self.data = {}

    def update(self,rabbitmq,data):
        self.last_active = time.time()
        self.rabbitmq = rabbitmq
        self.data = data

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
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'topic'
    QUEUE = 'squiddata'
    ROUTING_KEY = 'example.text'

    def __init__(self, amqp_url, shoal):
        self._connection = None
        self._channel = None
        self._consumer_tag = None
        self._url = amqp_url
        self.shoal = shoal

    def connect(self):
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open)

    def close_connection(self):
        self._connection.close()

    def add_on_connection_close_callback(self):
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, method_frame):
        self._channel = None
        self._connection = self.connect()

    def on_connection_open(self, unused_connection):
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_channel_close_callback(self):
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, method_frame):
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
        self._channel.queue_declare(self.on_queue_declareok, queue_name)

    def on_queue_declareok(self, method_frame):
        self._channel.queue_bind(self.on_bindok, self.QUEUE,
                                 self.EXCHANGE, self.ROUTING_KEY)

    def add_on_cancel_callback(self):
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        self._channel.close()

    def acknowledge_message(self, delivery_tag):
        self._channel.basic_ack(delivery_tag)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        self.process_message(basic_deliver, properties, body)

        self.acknowledge_message(basic_deliver.delivery_tag)

    def on_cancelok(self, unused_frame):
        self.close_connection()

    def stop_consuming(self):
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
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        self.stop_consuming()
        self._connection.ioloop.start()

    def process_message(self,basic_deliver, properties, body):
        rabbitmq = {'basic_deliver':basic_deliver, 'properties':properties, }
        data = json.loads(body)
        ip = data['ip']
        updated = False

        # update squid if exists in shoal
        for s in self.shoal:
            if s.ip == ip:
                s.update(rabbitmq,data)
                updated = True

        # if squid doesnt exist in shoal create new squid
        if not updated:
            new_squid = SquidNode(data['ip'])
            new_squid.data = data
            new_squid.rabbitmq = rabbitmq
            self.shoal.append(new_squid)

"""
    Main function to run Shoal.
"""
def main():
    app = Application()

if __name__ == '__main__':
    main()
