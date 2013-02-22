import web
import re
import geoip
import json
import operator
import config

from time import time

t_globals = dict(
  datestr=web.datestr,
)

CACHE = config.webpy_cache
TEMPLATES = config.webpy_template_dir


render = web.template.render(TEMPLATES, cache=CACHE, globals=t_globals)
render._keywords['globals']['render'] = render

def index(**k):
    squid_inactive_time = config.squid_inactive_time
    sorted_shoal = []

    sorted_shoal = sorted(web.shoal.values(), key=operator.attrgetter('last_active'))

    sorted_shoal.reverse()
    return render.index(sorted_shoal, squid_inactive_time, time())

def nearest(**k):
    if web.ctx.query:
        ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', web.ctx.query)[0]
    else:
        ip = web.ctx['ip']

    squid = geoip.get_nearest_squid(ip)
    web.header('Content-Type', 'application/json')
    if squid:
        squid_json = {'public_ip':squid.public_ip, 'private_ip':squid.private_ip,}
        return json.dumps(squid_json)
    else:
        squid_json = {'public_ip':None, 'private_ip':None,}
        return json.dumps(squid_json)
