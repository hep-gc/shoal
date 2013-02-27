import web
import view
from view import render

class index:
    def GET(self):
        return render.base(view.index())

class nearest:
    def GET(self):
        return view.nearest()
