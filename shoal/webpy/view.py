import web
import config
import re
import geoip

from time import time
from datetime import datetime

t_globals = dict(
  datestr=web.datestr,
  shoal=web.shoal,
)

ACTIVE_TIME = 180

render = web.template.render('webpy/templates/', cache=config.cache,globals=t_globals)
render._keywords['globals']['render'] = render

def index(**k):
    web.debug(web.shoal)
    return render.index(ACTIVE_TIME, now=time())

def nearest(**k):
    ip = web.ctx['ip']
    if web.ctx.query:
        ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', web.ctx.query)[0]

    squid = geoip.get_nearest_squid(ip)
    web.debug('public ip')
    web.debug(squid.data['public_ip'])
    if squid:
        return render.json(squid.data['public_ip'])
    else:
        return render.json(None)
