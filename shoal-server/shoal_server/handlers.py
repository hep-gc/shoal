import tornado.web
import time


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        shoal = self.application.shoal
        sorted_shoal = [shoal[k] for k in sorted(shoal, key=shoal.get, reverse=True)]
        inactive_time = self.application.global_settings['squid']['inactive_time']
        self.render("index.html", shoal=sorted_shoal, inactive_time=inactive_time, now=time.time())

class NearestHandler(tornado.web.RequestHandler):
    pass
