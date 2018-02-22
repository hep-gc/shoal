#!/usr/bin/env python
import sys
import json
import logging
import socket
import uuid
import urllib
from time import time, sleep
from threading import Thread

import web
import pika

from shoal_server import config
from shoal_server import utilities

# Basic class to store and update information about each squid server.
class SquidNode(object):

    def __init__(self, key, hostname, squid_port, public_ip, private_ip, external_ip, load, geo_data, verified, global_access, domain_access, drift_detected, drift_time, max_load=122000, last_active=time()):
        """
        constructor for SquidNode, time created is current time
        """
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
        self.verified = verified
        self.global_access = global_access
        self.domain_access = domain_access
        self.max_load = max_load
        self.drift_detected = drift_detected
        self.drift_time = drift_time
        self.last_verified = 0
        self.error = 'All systems OK!'

    def update(self, load, drift_detected, drift_time):
        """
        updates SquidNode with current time, load and drift detection boolean value
        """
        self.last_active = time()
        self.load = load
        self.drift_detected = drift_detected

    def jsonify(self):
        """
        returns a dictionary with current Squid data
        """
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
            "verified": self.verified,
            "global_access": self.global_access,
            "domain_access": self.domain_access,
            "max_load": self.max_load,},)

# Main application that will monitor RabbitMQ and ShoalUpdate threads.
class ThreadMonitor(Thread):

    def __init__(self, shoal):
        # constructor for ThreadMonitor, sets up and threads together RabbitMQConsumer
        # and ShoalUpdate threads, also checks and downloads update as needed

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

        #check if verification is turned on in config
        if config.squid_verification:
            verify_thread = SquidVerifier(self.shoal)
            verify_thread.daemon = True
            self.threads.append(verify_thread)


    def run(self):
        """
        runs ThreadMonitor threads
        """
        for thread in self.threads:
            logging.info("starting", thread)
            thread.start()
        while True:
            for thread in self.threads:
                if not thread.is_alive():
                    logging.error('%s died. Stopping application...', thread)
                    sys.exit(1)
            sleep(1)

    def stop(self):
        """
        stops ThreadMonitor threads
        """
        logging.info("Shutting down Shoal-Server... Please wait.")
        try:
            self.rabbitmq.stop()
            self.update.stop()
        except Exception as exc:
            logging.error(exc)
            sys.exit(1)
        finally:
            sleep(2)
        sys.exit()


# ShoalUpdate is used for trimming inactive squids every set interval.
class ShoalUpdate(Thread):

    INTERVAL = config.squid_cleanse_interval
    INACTIVE = config.squid_inactive_time

    def __init__(self, shoal):
        """ShoalUpdate
        constructor for ShoalUpdate, uses parent Thread constructor as well
        """
        Thread.__init__(self)
        self.shoal = shoal
        self.running = False

    def run(self):
        """
        runs ShoalUpdate
        """
        self.running = True
        while self.running:
            sleep(self.INTERVAL)
            self.update()

    def update(self):
        """
        updates and pops squid from shoal if it's inactive
        """
        curr = time()
        for squid in self.shoal.values():
            if curr - squid.last_active > self.INACTIVE:
                self.shoal.pop(squid.key)

    def stop(self):
        """
        stops ShoalUpdate
        """
        self.running = False

# Webpy webserver used to serve up active squid lists and API calls. Can run as either the development server or under mod_wsgi.
class WebpyServer(Thread):

    def __init__(self, shoal):
        # constructor for WebpyServer, uses parent Thread constructor as well,
        # and uses values from config file and web

        Thread.__init__(self)
        web.shoal = shoal
        web.config.debug = False
        self.app = None
        self.urls = (
            '/all/?(\d+)?/?', 'shoal_server.view.allsquids',
            '/nearest/?(\d+)?/?', 'shoal_server.view.nearest',
            '/nearestverified/?(\d+)?/?', 'shoal_server.view.nearestverified',
            '/wpad.dat', 'shoal_server.view.wpad',
            '/(\d+)?/?', 'shoal_server.view.index',
        )

    def run(self):
        """
        runs web application
        """
        try:
            self.app = web.application(self.urls, globals())
            self.app.run()
        except Exception as exc:
            logging.error("Could not start webpy server.\n%s", exc)
            sys.exit(1)

    def wsgi(self):
        """
        returns Web Server Gateway Interface for application
        """
        return web.application(self.urls, globals()).wsgifunc()

    def stop(self):
        """
        stops web application
        """
        self.app.stop()


# Basic RabbitMQ async consumer. Consumes messages from a unique queue that is declared
# when Shoal server first starts.
# The consumer takes the json in message body, and tracks it in the dictionary `shoal`
class RabbitMQConsumer(Thread):
    # sets defaults for RabbitMQ consumer
    QUEUE = socket.gethostname() + "-" + uuid.uuid1().hex
    EXCHANGE = config.amqp_exchange
    EXCHANGE_TYPE = config.amqp_exchange_type
    ROUTING_KEY = '#'
    INACTIVE = config.squid_inactive_time

    def __init__(self, shoal):
        # constructor for RabbitMQConsumer, uses parent Thread constructor as well,
        # and uses values from config file

        Thread.__init__(self)
        self.host = "{0}/{1}".format(config.amqp_server_url, urllib.quote_plus(config.amqp_virtual_host))
        self.shoal = shoal
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None

    def connect(self):
        """
        establishes a connection to the AMQP server with SSL options
        """
        # gets SSL options from config files
        failedConnectionAttempts = 0
        sslOptions = {}
        try:
            if config.use_ssl:
                sslOptions["ca_certs"] = config.amqp_ca_cert
                sslOptions["certfile"] = config.amqp_client_cert
                sslOptions["keyfile"] = config.amqp_client_key
        except Exception as exc:
            logging.error("Could not read SSL files")
            logging.error(exc)

        # tries to establish a connection with AMQP server
        # will retry a number of times before passing the exception up
        while True:
            try:
                connection = pika.SelectConnection(
                    pika.ConnectionParameters(
                        host=config.amqp_server_url,
                        port=config.amqp_port,
                        ssl=config.use_ssl,
                        ssl_options=sslOptions
                        ),
                    self.on_connection_open,
                    stop_ioloop_on_close=False)
                return connection
            except pika.exceptions.AMQPConnectionError as exc:
                failedConnectionAttempts += 1
                if failedConnectionAttempts >= config.error_reconnect_attempts:
                    logging.error(
                        "Was not able to establish connection to AMQP server after %s attempts.",
                        failedConnectionAttempts)
                    logging.error(exc)
                    raise exc
                logging.error(
                    "Could not connect to AMQP Server. Retrying in %s seconds...",
                    config.error_reconnect_time)
                sleep(config.error_reconnect_time)
                continue

    def close_connection(self):
        """
        closes connections with AMQP server
        """
        self._connection.close()

    def add_on_connection_close_callback(self):
        """
        adds a connection and closes callback
        """
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """
        stops IO connection loop
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logging.warning(
                'Connection closed, reopening in 5 seconds: (%s) %s',
                reply_code,
                reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def on_connection_open(self, unused_connection):
        """
        opens channel and connection
        """
        self.add_on_connection_close_callback()
        self.open_channel()

    def reconnect(self):
        """
        stops current IO loop and then reconnects
        """
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()
        if not self._closing:
            # Create a new connection
            self._connection = self.connect()
            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def add_on_channel_close_callback(self):
        """
        adds a channel and closes callback
        """
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """
        closes connection on channel
        """
        logging.warning('Channel was closed: (%s) %s', reply_code, reply_text)
        self._connection.close()

    def on_channel_open(self, channel):
        """
        opens connection on channel
        """
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def setup_exchange(self, exchange_name):
        """
        establishes exchange
        """
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        """
        callback for exchange
        """
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        """
        establishes queue, automatically deletes after disconnecting
        """
        self._channel.queue_declare(self.on_queue_declareok, queue_name, auto_delete=True)

    def on_queue_declareok(self, method_frame):
        """
        callback for queue
        """
        self._channel.queue_bind(self.on_bindok, self.QUEUE,
                                 self.EXCHANGE, self.ROUTING_KEY)

    def add_on_cancel_callback(self):
        """
        cancels callback
        """
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """
        closes channel on consumer
        """
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        """
        acknowledges that consumer has received the message
        """
        self._channel.basic_ack(delivery_tag)

    def on_cancelok(self, unused_frame):
        """
        calls close channel
        """
        self.close_channel()

    def stop_consuming(self):
        """
        stops consuming, exits out of basic consume
        """
        if self._channel:
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def start_consuming(self):
        """
        starts consuming registered callbacks
        """
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.QUEUE)

    def on_bindok(self, unused_frame):
        """
        callback for bind
        """
        self.start_consuming()

    def close_channel(self):
        """
        closes channel
        """
        self._channel.close()

    def open_channel(self):
        """
        opens channel
        """
        self._connection.channel(on_open_callback=self.on_channel_open)

    def run(self):
        """
        sets up connection and starts IO loop
        """
        try:
            self._connection = self.connect()
        except Exception as exc:
            logging.error("Unable to connect ot RabbitMQ Server. %s", exc)
            sys.exit(1)
        try:
            self._connection.ioloop.start()
        except Exception as exc:
            logging.error("rabbitmq connection died %s", exc)

    def stop(self):
        """
        stops consuming and closes IO loop
        """
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """
        Retreives information from data, and then updates each squid load in
        shoal if the public/private ip matches. Shoal's key will update with
        the load if there's a key in Shoal. geo_data will update or create a
        new SquidNode if the time since the last timestamp is less than the
        inactive time and a public/private ip exists
        """
        external_ip = public_ip = private_ip = None
        #assume global access unless otherwise indicated
        globalaccess = domainaccess = True
        drift_detected = False
        drift_time = 0
        curr = time()

        # extracts information from data from body
        try:
            data = json.loads(body)
        except ValueError:
            logging.error("Message body could not be decoded. Message: %s", body[1])
            self.acknowledge_message(basic_deliver.delivery_tag)
            return
        try:
            key = data['uuid']
            hostname = data['hostname']
            time_sent = data['timestamp']
            load = data['load']
            squid_port = data['squid_port']

        except KeyError as exc:
            logging.error(
                "Message received was not the proper format (missing:%s), discarding...", exc)
            self.acknowledge_message(basic_deliver.delivery_tag)
            return
        try:
            external_ip = data['external_ip']
        except KeyError:
            pass
        try:
            public_ip = data['public_ip']
        except KeyError:
            public_ip = external_ip
        try:
            private_ip = data['private_ip']
        except KeyError:
            pass
        try:
            verified = data['verified']
        except KeyError:
            verified = config.squid_verified_default
        try:
            maxload = data['max_load']
        except KeyError:
            maxload = config.squid_max_load
        try:
            globalaccess = bool('True' in data['global_access'])
        except KeyError:
            pass
        try:
            domainaccess = bool('True' in data['domain_access'])
        except KeyError:
            pass

        # attempt to detect misconfigured clocks and clock drifts,
        # allows for a 10 second grace period
        if curr - time_sent > 10:
            logging.error(
                "Potential clock drift dectected: %s second descrepency on %s",
                (curr-time_sent),
                public_ip)
            drift_detected = True
        elif curr - time_sent < -10:
            logging.error(
                "Recived message from %s seconds in the future from %s",
                (-1*(curr-time_sent)),
                public_ip)
            drift_detected = True
        # this else is redundant because the var is initally set to
        # false but this works well as a failsafe
        else:
            drift_detected = False
        drift_time = (curr-time_sent)

        # if there's a key in shoal, shoal's key will update with the load and drift detection
        if key in self.shoal:
            self.shoal[key].update(load, drift_detected, drift_time)
        # if the difference in time since the last timestamp is less than the inactive time
        # and there exists a public or private ip, then the geo_data will update its location
        # or create a new SquidNode for shoal if the geo_data doesn't exist
        elif (curr - time_sent < self.INACTIVE) and (public_ip or private_ip):
            geo_data = utilities.get_geolocation(public_ip)
            if not geo_data:
                geo_data = utilities.get_geolocation(external_ip)
            if not geo_data:
                logging.error("Unable to generate geo location data, discarding message")
            else:
                new_squid = SquidNode(
                    key,
                    hostname,
                    squid_port,
                    public_ip,
                    private_ip,
                    external_ip,
                    load,
                    geo_data,
                    verified,
                    globalaccess,
                    domainaccess,
                    drift_detected,
                    drift_time,
                    maxload,
                    time_sent)
                self.shoal[key] = new_squid
        self.acknowledge_message(basic_deliver.delivery_tag)


# SquidVerifier runs on an interval specified in the config file. Each interval it checks each
# squid saves to the server to make sure it is ready for traffic and is servering files.
# If a squid isn't responding to requests it is removed from the server, otherwise it is
# tagged as verified.
class SquidVerifier(Thread):

    INTERVAL = config.squid_verify_interval

    def __init__(self, shoal):
        """SquidVerifier
        constructor for SquidVerifier, uses parent Thread constructor as well
        """
        Thread.__init__(self)
        self.shoal = shoal
        self.running = False

    def run(self):
        """
        runs verify
        """
        INTERVAL = config.squid_verify_interval
        self.running = True
        while self.running:
            for squid in web.shoal.values():
                current_time = time()
                # In an ideal scenario shoal would continuously try to verify those
                # that are not verified. However since many squids use old agents
                # its likely that they are not configured correctly and this would
                # make the verification loop try and verify them over and over when
                # they can't be. Instead they will be verified once every interval
                # greatly reducing computing resource requirements for misconfigured agents.
                if (current_time - squid.last_verified) >= INTERVAL:
                    utilities.verify(squid)
                    squid.last_verified = time()

    def stop(self):
        """
        stops Squid_Verifier
        """
        self.running = False
