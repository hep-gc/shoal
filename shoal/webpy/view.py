import web
import re
import geoip

from time import time
from datetime import datetime

t_globals = dict(
  datestr=web.datestr,
  shoal=web.shoal,
)

ACTIVE_TIME = 180

render = web.template.render('webpy/templates/', cache=True,globals=t_globals)
render._keywords['globals']['render'] = render

def index(**k):
    return render.index(ACTIVE_TIME, now=time())

def nearest(**k):
    if web.ctx.query:
        ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', web.ctx.query)[0]
    else:
        ip = web.ctx['ip']

    squid = geoip.get_nearest_squid(ip)

    if squid:
        return render.json(squid.data['public_ip'])
    else:
        return render.json(None)
