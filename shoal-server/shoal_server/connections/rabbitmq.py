import json
import logging
import pika
import socket
import urllib
import uuid
import utilities

from time import time
from pika import adapters

class Consumer(object):
    """
        Basic RabbitMQ async consumer. Consumes messages from a unique queue that is declared when Shoal server first starts.
        The consumer takes the json in message body, and tracks it in the dictionary `shoal`
    """
    def __init__(self, settings, shoal):
        """constructor for RabbitMQConsumer, uses values from settings file"""
        self.host = "{0}/{1}".format(settings['rabbitmq']['host'],
                                     urllib.quote_plus(settings['rabbitmq']['virtual_host']))
        #self.shoal = shoal
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._settings = settings
        self.shoal = shoal

        self.queue = socket.gethostname() + "-" + uuid.uuid1().hex
        self.exchange = settings['rabbitmq']['exchange']
        self.exchange_type = settings['rabbitmq']['exchange_type']
        self.routing_key = '#'
        self.inactive = settings['squid']['inactive_time']

    def connect(self):
        """establishes a connection to the AMQP server with SSL options"""
        # gets SSL options from settings files
        failed_connection_attempts = 0
        ssl_options = {}
        try:
            if self._settings['rabbitmq']['use_ssl']:
                logging.debug("Using SSL")
                ssl_options = {
                    "ca_certs": self._settings['rabbitmq']['ca_cert'],
                    "certfile": self._settings['rabbitmq']['client_cert'],
                    "keyfile":  self._settings['rabbitmq']['client_key'],
                }
        except Exception as e:
            logging.error("Could not read SSL files")
            logging.error(e)

        logging.debug("Connecting to %s", self._settings["rabbitmq"]["host"])
        connection = adapters.TornadoConnection(pika.ConnectionParameters(
                                             host=self._settings['rabbitmq']['host'],
                                             port=self._settings['rabbitmq']['port'],
                                             ssl=self._settings['rabbitmq']['use_ssl'],
                                             ssl_options = ssl_options
                                           ),
                                           self.on_connection_open,
                                           stop_ioloop_on_close=False)
        return connection

    def on_connection_open(self, unused_connection):
        """opens channel and connection"""
        logging.debug("connection opened.")
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """stops IO connection loop"""
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logging.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def close_connection(self):
        """closes connections with AMQP server"""
        logging.debug("closing connection.")
        self._connection.close()

    def reconnect(self):
        """stops current IO loop and then reconnects"""
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()
        if not self._closing:
            # Create a new connection
            self._connection = self.connect()
            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def on_channel_open(self, channel):
        """opens connection on channel"""
        logging.debug("channel opened.")
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)

        # setup the exchange
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       self.exchange,
                                       self.exchange_type)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """closes connection on channel"""
        logging.warning('Channel was closed: (%s) %s', reply_code, reply_text)
        self._connection.close()

    def on_exchange_declareok(self, unused_frame):
        """callback for exchange"""
        logging.debug("exchange declared")
        # setup queue
        self._channel.queue_declare(self.on_queue_declareok, self.queue, auto_delete=True)

    def on_queue_declareok(self, method_frame):
        """callback for queue"""
        logging.debug("binding %s to %s with %s",
                        self.exchange, self.queue, self.routing_key)
        self._channel.queue_bind(self.start_consuming, self.queue,
                                 self.exchange, self.routing_key)

    def on_consumer_cancelled(self, method_frame):
        """closes channel on consumer"""
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        """acknowledges that consumer has received the message"""
        self._channel.basic_ack(delivery_tag)

    def on_cancelok(self, unused_frame):
        """calls close channel"""
        self.close_channel()

    def stop_consuming(self):
        """stops consuming, exits out of basic consume"""
        if self._channel:
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def start_consuming(self, unused_frame):
        """starts consuming registered callbacks"""
        # add cancel callback
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.queue)
    def close_channel(self):
        """closes channel"""
        self._channel.close()

    def run(self):
        """sets up connection and starts IO loop"""
        try:
            self._connection = self.connect()
        except Exception as e:
            logging.error("Unable to connect to RabbitMQ Server. {0}".format(e))
            sys.exit(1)
        self._connection.ioloop.start()

    def stop(self):
        """stops consuming and closes IO loop"""
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Retreives information from data, and then updates each squid load in
           shoal if the public/private ip matches. Shoal's key will update with
           the load if there's a key in Shoal. geo_data will update or create a
           new SquidNode if the time since the last timestamp is less than the
           inactive time and a public/private ip exists"""
        print "GOT A MESSAGE"
        external_ip = public_ip = private_ip = None
        curr = time()

        # extracts information from body of AMQP message
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
            public_ip = data['public_ip']
        except KeyError:
            pass
        try:
            external_ip = data['external_ip']
        except KeyError:
            pass
        try:
            private_ip = data['private_ip']
        except KeyError:
            pass

        # for each squid in shoal, if public or private ip matches,
        # load for the squid will update and send a acknowledgment message
        for squid in self.shoal.values():
           if squid["public_ip"] == public_ip or squid["private_ip"] == private_ip:
              squid.update({"load": data["load"]})
              self.acknowledge_message(basic_deliver.delivery_tag)
              return

        # if there's a key in shoal, shoal's key will update with the load
        if key in self.shoal:
            self.shoal[key].update(load)
        # if the difference in time since the last timestamp is less than the inactive time
        # and there exists a public or private ip, then the geo_data will update its location
        # or create a new SquidNode for shoal if the geo_data doesn't exist
        elif (curr - time_sent < self.inactive) and (public_ip or private_ip):
            """DISABLED DUE TO MAXMIND DATABASE API UPDATE"""
            #geo_data = utilities.get_geolocation(public_ip)
            #if not geo_data:
            #    geo_data = utilities.get_geolocation(external_ip)
            #if not geo_data:
            #    logging.error("Unable to generate geo location data, discarding message")
            #else:
            """END DISABLE"""
            data["last_active"] = time()
            self.shoal[key] = data

        self.acknowledge_message(basic_deliver.delivery_tag)
