import config
import connections
import logging
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
        # Setup connections, pass io_loop and config
        self.conn = connections.setup(config.settings, io_loop)

        tornado.web.Application.__init__(self, handlers, **config.settings['general'])


def run():
    io_loop = tornado.ioloop.IOLoop.instance()

    # pass io_loop so connections(pika) can hook into it.
    app = Application(io_loop)
    app.listen(config.settings['general']['port'])

    io_loop.start()

run()
