import web
import re
import json
import operator
import config
import math

from time import time
from shoal_server import utilities
from __version__ import version

t_globals = dict(
  datestr=web.datestr,
  version=version,
  squid_active_time=config.squid_inactive_time,
)

CACHE = config.webpy_cache
TEMPLATES = 'templates/'

render = web.template.render(TEMPLATES, cache=CACHE, globals=t_globals)
render._keywords['globals']['render'] = render

class index:
    def GET(self, size):
        return render.base(view_index(size))

class nearest:
    def GET(self, count):
        web.header('Content-Type', 'application/json')
        return view_nearest(count)
    
class nearestverified:
    def GET(self, count):
        web.header('Content-Type', 'application/json')
        return view_nearest_verified(count)

class allsquids:
    def GET(self, count):
        web.header('Content-Type', 'application/json')
        return view_allsquids()

class wpad:
    def GET(self):

        # note view_wpad does not return a string
        data = str(view_wpad())
        web.header('Content-Type', 'application/x-ns-proxy-autoconfig')
        web.header('Content-Length',len(data))
        return data

def view_index(size):
    """
        returns an index template with a sorted_shoal list with upper
        and lower bounds from the given size
    """
    params = web.input()
    page = params.page if hasattr(params, 'page') else 1
    sorted_shoal = sorted(web.shoal.values(), key=operator.attrgetter('last_active')) 
    sorted_shoal.reverse()
    total = len(sorted_shoal)
    page = int(page)

      
    try:
        size = int(size)
    except (ValueError, TypeError):
        size = 20
    try:
        pages = int(math.ceil(len(sorted_shoal) / float(size)))
    except ZeroDivisionError:
        return render.index(time(), total, sorted_shoal, 1, 1, 0)

    if page < 1:
        page = 1
    if page > pages:
        page = pages

    lower, upper = int(size * (page - 1)), int(size * page)
    return render.index(time(), total, sorted_shoal[lower:upper], page, pages, size)

def view_nearest(count):
    """
        returns the nearest squid as a JSON formatted str
    """
    try:
        count = int(count)
    except (ValueError, TypeError):
        count = 5

    ip = web.ctx['ip']

    squids = utilities.get_nearest_squids(ip,count)
    if squids:
        squid_json = {}
        for i,squid in enumerate(squids):
            squid_json[i] = squid[0].jsonify()
            squid_json[i]['distance'] = squid[1]
        return json.dumps(squid_json)
    else:
        return json.dumps(None)

def view_nearest_verified(count):
    """
        returns the nearest squid as a JSON formatted str
    """
    try:
        count = int(count)
    except (ValueError, TypeError):
        count = 5

    ip = web.ctx['ip']

    squids = utilities.get_nearest_verified_squids(ip,count)
    if squids:
        squid_json = {}
        for i,squid in enumerate(squids):
            squid_json[i] = squid[0].jsonify()
            squid_json[i]['distance'] = squid[1]
        return json.dumps(squid_json)
    else:
        return json.dumps(None)

def view_allsquids():
    """
        returns the all squids as a JSON formatted str
    """
    squids = utilities.get_all_squids()
    if squids:
        squid_json = {}
        for i,squid in enumerate(squids):
            squid_json[i] = squid.jsonify()
        return json.dumps(squid_json)
    else:
        return json.dumps(None)

def view_wpad(**k):
    """
        returns data as a wpad
    """
    data = render.wpad(utilities.generate_wpad(web.ctx['ip']))
    return data
