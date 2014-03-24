import connections
import logging
import time
import tornado.web
import tornado.ioloop
import utilities

from handlers import IndexHandler, NearestHandler, AllSquidHandler
from os.path import join


class Application(tornado.web.Application):
    def __init__(self, settings, io_loop):
        handlers = [
            (r"/", IndexHandler),
            (r"/nearest", NearestHandler),
            (r"/nearest/?(\d+)?/?", NearestHandler),
            (r"/all", AllSquidHandler),
        ]
        self.global_settings = settings
        self.shoal = {}

        # Setup Redis Connection
        logging.info("Setting up Redis connection...")
        self.redis = connections.setup_redis(self.global_settings)
        logging.info("complete.")

        # setup rabbitmq connection
        logging.info("Setting up RabbitMQ Consumer...")
        self.rabbitmq = connections.setup_rabbitmq(self.global_settings, self.shoal)
        logging.info("complete.")

        # setup periodic squid cleanse (configurable).
        logging.info("Setting up Periodic Callback to remove inactive Squids ( %ds ) every %ds...",
            settings["squid"]["inactive_time"],
            settings["squid"]["cleanse_interval"])
        tornado.ioloop.PeriodicCallback(self.cleanse,
                settings["squid"]["cleanse_interval"]*1000,
                io_loop=io_loop).start()
        logging.info("complete.")

        # GeoIP database initialize
        if utilities.check_geolitecity_need_update(settings['general']['geolitecity_path'],
                settings['general']['geolitecity_update']):
            utilities.download_geolitecity(settings['general']['geolitecity_url'],
                settings['general']['geolitecity_path'], settings['general']['geolitecity_update'])
        tornado.web.Application.__init__(self, handlers, **self.global_settings['tornado'])

    # Cleans up the inactive squids. Runs periodically.
    def cleanse(self):
        """updates and pops squid from shoal if it's inactive"""
        curr = time.time()
        for squid in self.shoal.values():
            if curr - squid["last_active"] > self.global_settings["squid"]["inactive_time"]:
                logging.info("Removing inactive squid (%s) %s from shoal.", squid["uuid"], squid["hostname"])
                self.shoal.pop(squid["uuid"])
