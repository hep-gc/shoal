import tornado.web
import config


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.application.shoal)

class NearestHandler(tornado.web.RequestHandler):
    pass
