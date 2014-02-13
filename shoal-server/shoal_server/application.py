import config
import connections
import tornado.web
import tornado.ioloop
from handlers import IndexHandler, NearestHandler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/nearest(/\d+)?/?$", NearestHandler),
        ]
        self.global_settings = config.settings
        # Setup connections, pass io_loop and config
        self.conn = connections.setup(config.settings, io_loop)

        tornado.web.Application.__init__(self, handlers, **config.settings['general'])

if __name__ == "__main__":
    io_loop = tornado.ioloop.IOLoop.instance()

    # pass io_loop so connections(pika) can hook into it.
    app = Application()
    app.listen(config.settings['general']['port'])
    io_loop.start()

