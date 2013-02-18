import web
import re
import geoip
import json
import operator

from time import time
from datetime import datetime

t_globals = dict(
  datestr=web.datestr,
)

ACTIVE_TIME = 180

render = web.template.render('webpy/templates/', cache=False, globals=t_globals)
render._keywords['globals']['render'] = render

def index(**k):
    web.debug(web.shoal)
    sorted_shoal = []

    for squid in (sorted(web.shoal.values(), key=operator.attrgetter('last_active'))):
        sorted_shoal.append(squid)

    sorted_shoal.reverse()
    web.debug(sorted_shoal)
    return render.index(sorted_shoal, ACTIVE_TIME, now=time())

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
