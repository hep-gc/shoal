import tornado.web
from utilities import get_nearest_squids


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.application.global_settings)


class NearestHandler(tornado.web.RequestHandler):
    def get(self):
        ip = self.request.remoteip
        squid = get_nearest_squids(ip)
        self.write(squid)

