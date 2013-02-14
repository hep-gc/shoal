import web
import view, restful, config
from view import render

class index:
    def GET(self):
        return render.base(view.index())
class nearest:
    def GET(self):
        web.response('Content-Type', 'application/json')
        return render.blank(restful.nearest())
