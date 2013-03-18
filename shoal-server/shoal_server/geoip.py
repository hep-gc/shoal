import sys
import os
import subprocess
import pygeoip
import web
import logging
import operator
from time import time, sleep
from math import radians, cos, sin, asin, sqrt

import config

"""
    Given an IP return all its geographical information (using GeoLiteCity.dat)
"""
def get_geolocation(ip):
    geolitecity_path = config.geolitecity_path
    try:
        gi = pygeoip.GeoIP(geolitecity_path)
        return gi.record_by_addr(ip)
    except Exception as e:
        logging.error(e)
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

    smallest_distance = float("inf")
    nearest_squids = {}

    for squid in web.shoal.values():
        s_lat = float(squid.geo_data['latitude'])
        s_long = float(squid.geo_data['longitude'])

        distance = haversine(r_lat,r_long,s_lat,s_long)

        nearest_squids[squid.key] = {'distance':distance, 'public_ip':squid.public_ip, 'private_ip':squid.private_ip, 'hostname':squid.hostname,}

    squids = sorted(nearest_squids.values(), key=nearest_squids.get('distance'))

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

    return r * c

def check_geolitecity_need_update():
    curr = time()
    geolitecity_update = config.geolitecity_update
    geolitecity_path = config.geolitecity_path

    if os.path.exists(geolitecity_path):
        if curr - os.path.getmtime(geolitecity_path) < geolitecity_update:
            logging.info('GeoLiteCity is up-to-date')
            return False
        else:
            logging.warning('GeoLiteCity database needs updating.')
            return True
    else:
        logging.warning('GeoLiteCity database needs updating.')
        return True

def download_geolitecity():
    geolitecity_path = config.geolitecity_path

    cmd = ['wget','-O','{0}.gz'.format(geolitecity_path),config.geolitecity_url]
    ungz = ['gunzip','-f','{0}.gz'.format(geolitecity_path)]

    try:
        dl = subprocess.Popen(cmd)
        dl.wait()
        gz = subprocess.Popen(ungz)
        gz.wait()

        if check_geolitecity_need_update():
            logging.error('GeoLiteCity database failed to update.')

    except Exception as e:
        logging.error("Could not download the database. - {0}".format(e))
        sys.exit(1)
