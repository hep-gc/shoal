import web
import view
from view import render

class index:
    def GET(self, size):
        return render.base(view.index(size))

class nearest:
    def GET(self, count):
        return view.nearest(count)

class external_ip:
    def GET(self):
        return view.external_ip()

class wpad:
    def GET(self):
        return view.wpad_generator()
