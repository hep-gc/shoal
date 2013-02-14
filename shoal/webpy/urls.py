import web
import view, config
from view import render

class index:
    def GET(self):
        return render.base(view.index())
