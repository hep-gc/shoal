import web
import view
from view import render

urls = (
    '/', 'urls.index',
    '/nearest', 'urls.nearest',
)

class index:
    def GET(self):
        return render.base(view.index())

class nearest:
    def GET(self):
        return view.nearest()
