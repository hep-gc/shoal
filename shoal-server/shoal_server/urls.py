import web
import view
from view import render

class index:
    def GET(self, size):
        return render.base(view.index(size))

class nearest:
    def GET(self):
        return view.nearest()

class external_ip:
    def GET(self):
        return view.external_ip()
