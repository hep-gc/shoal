import json
import tornado.web
import time
from utilities import get_nearest_squids
from tornado import gen


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        shoal = self.application.shoal
        sorted_shoal = [shoal[k] for k in sorted(shoal.keys(), key=lambda key: shoal[key]['last_active'], reverse=True)]
        inactive_time = self.application.global_settings['squid']['inactive_time']
        self.render("index.html", shoal=sorted_shoal, inactive_time=inactive_time, now=time.time())


class NearestHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, count=10):
        squids = yield gen.Task(
            get_nearest_squids,
            self.application.shoal,
            self.application.global_settings['general']['geolitecity_path'],
            self.request.remote_ip,
            count=count
        )

        if squids:
            self.write(json.dumps(squids))
        else:
            json.dumps({})
        self.finish()

class AllSquidHandler(tornado.web.RequestHandler):
    def get(self):
        shoal = self.application.shoal
        sorted_shoal = [shoal[k] for k in sorted(shoal.keys(), key=lambda key: shoal[key]['last_active'], reverse=True)]

        self.write(json.dumps(sorted_shoal))
