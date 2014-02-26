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
        self.redis = connections.setup_redis(self.global_settings)

        # setup rabbitmq connection
        self.rabbitmq = connections.setup_rabbitmq(self.global_settings, self.shoal)

        # setup periodic squid cleanse (5 seconds).
        tornado.ioloop.PeriodicCallback(self.cleanse,
                self.global_settings["squid"]["cleanse_interval"]*1000,
                io_loop=io_loop).start()

        tornado.web.Application.__init__(self, handlers, **config.settings['general'])

    # Cleans up the inactive squids. Runs periodically.
    def cleanse(self):
        """updates and pops squid from shoal if it's inactive"""
        curr = time.time()
        print "cleaning your squeeds"
        for squid in self.shoal.values():
            if curr - squid.last_active > self.INACTIVE:
                self.shoal.pop(squid.key)

def run():
    io_loop = tornado.ioloop.IOLoop.instance()

    # pass io_loop so connections(pika) can hook into it.
    app = Application(io_loop)

    # Hook RabbitMQ consumer into Tornado IOLoop
    io_loop.add_timeout(time.time() + .1, app.rabbitmq.run)

    app.listen(config.settings['general']['port'])

    io_loop.start()

run()
