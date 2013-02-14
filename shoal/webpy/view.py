import web
import config
import time
from datetime import datetime

t_globals = dict(
  datestr=web.datestr,
)

ACTIVE_TIME = 180

render = web.template.render('webpy/templates/', cache=config.cache,globals=t_globals)
render._keywords['globals']['render'] = render

def index(**k):
    data = {}
    curr = time.time()
    web.debug(web.shoal)
    local_shoal = web.shoal

    for s in local_shoal:
        if curr - s.last_active > ACTIVE_TIME:
            web.shoal.remove(s)

    for s in web.shoal:
        data[s.ip] = s.data

    return render.index(web.storage(data),ACTIVE_TIME)
