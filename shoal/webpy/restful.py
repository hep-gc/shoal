import web
import pygeoip
import re

def nearest(**k):
    ip = ''
    if web.ctx.query:
        ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', web.ctx.query)
    if not ip:
        ip = web.ctx['ip']


