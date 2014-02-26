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

        tornado.web.Application.__init__(self, handlers, **config.settings['general'])


def run():
    io_loop = tornado.ioloop.IOLoop.instance()

    # pass io_loop so connections(pika) can hook into it.
    app = Application(io_loop)
    io_loop.add_timeout(time.time() + .1, app.rabbitmq.run)
    app.listen(config.settings['general']['port'])

    io_loop.start()

run()
