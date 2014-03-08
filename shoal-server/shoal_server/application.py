import config
import connections
import logging
import time
import tornado.web
import tornado.ioloop

from handlers import IndexHandler, NearestHandler
from os.path import join


class Application(tornado.web.Application):
    def __init__(self, io_loop):
        handlers = [
            (r"/", IndexHandler),
            (r"/nearest", NearestHandler),
        ]
        self.global_settings = config.settings
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
            self.global_settings["squid"]["inactive_time"],
            self.global_settings["squid"]["cleanse_interval"])
        tornado.ioloop.PeriodicCallback(self.cleanse,
                self.global_settings["squid"]["cleanse_interval"]*1000,
                io_loop=io_loop).start()
        logging.info("complete.")

        tornado.web.Application.__init__(self, handlers, **config.settings['tornado'])

    # Cleans up the inactive squids. Runs periodically.
    def cleanse(self):
        """updates and pops squid from shoal if it's inactive"""
        curr = time.time()
        for squid in self.shoal.values():
            if curr - squid["last_active"] > self.global_settings["squid"]["inactive_time"]:
                logging.info("Removing inactive squid (%s) %s from shoal.", squid["uuid"], squid["hostname"])
                self.shoal.pop(squid["uuid"])


def run():
    io_loop = tornado.ioloop.IOLoop.instance()

    # pass io_loop so connections(pika) can hook into it.
    app = Application(io_loop)

    # Hook RabbitMQ consumer into Tornado IOLoop
    logging.info("Hooking RabbitMQ Consumer into IOLoop...")
    io_loop.add_timeout(time.time() + .1, app.rabbitmq.run)
    logging.info("complete.")

    logging.info("Starting Tornado on Port %s", config.settings['tornado']['port'])
    app.listen(config.settings['tornado']['port'])

    io_loop.start()

run()
