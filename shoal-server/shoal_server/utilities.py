import sys
import os
import subprocess
import pygeoip
import web
import logging
import operator
import gzip
from time import time, sleep
from math import radians, cos, sin, asin, sqrt
from urllib import urlretrieve

import config

GEOLITE_DB = os.path.join(config.geolitecity_path,"GeoLiteCity.dat")
GEOLITE_URL = config.geolitecity_url
GEOLITE_UPDATE = config.geolitecity_update

logger = logging.getLogger('shoal_server')
"""
    Given an IP return all its geographical information (using GeoLiteCity.dat)
"""
def get_geolocation(ip):
    try:
        gi = pygeoip.GeoIP(GEOLITE_DB)
        return gi.record_by_addr(ip)
    except Exception as e:
        logger.error(e)
        return None

"""
    Given an IP return IP of nearest squid.
"""
def get_nearest_squids(ip, count=10):
    request_data = get_geolocation(ip)
    if not request_data:
        return None

    r_lat = request_data['latitude']
    r_long = request_data['longitude']

    nearest_squids = []

    for squid in web.shoal.values():
        s_lat = float(squid.geo_data['latitude'])
        s_long = float(squid.geo_data['longitude'])

        distance = haversine(r_lat,r_long,s_lat,s_long)

        nearest_squids.append((squid,distance))

    squids = sorted(nearest_squids, key=lambda k: (k[1], k[0].load))
    return squids[:count]

"""
    Calculate distance between two points using Haversine Formula.
"""
def haversine(lat1,lon1,lat2,lon2):
    # radius of earth
    r = 6371

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    return round((r * c),2)

def check_geolitecity_need_update():
    curr = time()

    if os.path.exists(GEOLITE_DB):
        if curr - os.path.getmtime(GEOLITE_DB) < GEOLITE_UPDATE:
            logger.info('GeoLiteCity is up-to-date')
            return False
        else:
            logger.warning('GeoLiteCity database needs updating.')
            return True
    else:
        logger.warning('GeoLiteCity database needs updating.')
        return True

def download_geolitecity():
    try:
        urlretrieve(GEOLITE_URL,GEOLITE_DB + '.gz')
    except Exception as e:
        logger.error("Could not download the database. - {0}".format(e))
        sys.exit(1)
    try:
        content = gzip.open(GEOLITE_DB + '.gz').read()
    except Exception as e:
        logger.error("GeoLiteCity.dat file was not properly downloaded. Check contents of {} for possible errors.".format(GEOLITE_DB + '.gz'))
        sys.exit(1)

    with open(GEOLITE_DB,'w') as f:
        f.write(content)

    if check_geolitecity_need_update():
        logger.error('GeoLiteCity database failed to update.')

def generate_wpad(ip):
    squids = get_nearest_squids(ip)
    if squids:
        proxy_str = ''
        for squid in squids:
            try:
                proxy_str += "PROXY http://{0}:{1};".format(squid[0].hostname,squid[0].squid_port)
            except TypeError as e:
                continue
        return proxy_str
    else:
        return None
