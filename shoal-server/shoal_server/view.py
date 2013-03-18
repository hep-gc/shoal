import web
import re
import geoip
import json
import operator
import config
import math
import wpad

from time import time

t_globals = dict(
  datestr=web.datestr,
  squid_active_time=config.squid_inactive_time,
)

CACHE = config.webpy_cache
TEMPLATES = 'templates/'

render = web.template.render(TEMPLATES, cache=CACHE, globals=t_globals)
render._keywords['globals']['render'] = render

def get_slices(page, page_size=100):
    return (int(page_size * (page - 1)), int((page_size * page)))

def index(size):
    params = web.input()
    page = params.page if hasattr(params, 'page') else 1
    sorted_shoal = sorted(web.shoal.values(), key=operator.attrgetter('last_active'))
    sorted_shoal.reverse()
    total = len(sorted_shoal)

    try:
        size = int(size)
    except (ValueError, TypeError):
        size = 20
    page = int(page)
    try:
        pages = int(math.ceil(len(sorted_shoal) / float(size)))
    except ZeroDivisionError:
        return render.index(time(), total, sorted_shoal, 1, 1, 0)

    if page < 1:
        page = 1
    if page > pages:
        page = pages

    lower, upper = get_slices(page,size)
    return render.index(time(), total, sorted_shoal[lower:upper], page, pages, size)

def nearest(count):
    try:
        count = int(count)
    except (ValueError, TypeError):
        count = 5

    if web.ctx.query:
        try:
            ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', web.ctx.query)[0]
        except IndexError:
            ip = None
    else:
        ip = web.ctx['ip']

    squids = geoip.get_nearest_squids(ip,count)

    web.header('Content-Type', 'application/json')

    if squids:
        squid_json = {}
        for i,squid in enumerate(squids):
            squid_json[i] = squid
        squid_json = json.dumps(squid_json)
        web.header('Content-Length', len(squid_json))
        return squid_json
    else:
        web.header('Content-Length', 4)
        return json.dumps(None)

def external_ip(**k):
    ip = web.ctx['ip']
    return json.dumps({'external_ip':ip,})

def wpad_generator(**k):
    data = render.wpad(wpad.generate_wpad(web.ctx['ip']))
    web.header('Content-Type', 'application/x-ns-proxy-autoconfig')
    web.header('Content-Length', len(data['__body__']))
    return data
