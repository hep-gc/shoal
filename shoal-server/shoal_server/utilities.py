import sys
import os
import subprocess
import pygeoip
import logging
import operator
import gzip
from time import time, sleep
from math import radians, cos, sin, asin, sqrt
from urllib import urlretrieve
from tornado import gen


def get_geolocation(db_path, ip):
    """
        Given an IP return all its geographical information (using GeoLiteCity.dat)
    """
    try:
        gi = pygeoip.GeoIP(db_path)
        return gi.record_by_addr(ip)
    except Exception as e:
        logging.error(e)
        return None

@gen.engine
def calculate_distance(db_path, ip, shoal, callback=None):
    """
        Given an IP return a sorted list of nearest squids up to a given count
    """
    request_data = get_geolocation(db_path, ip)
    #request_data = get_geolocation(db_path, '142.142.0.0')
    if not request_data:
        callback(None)
    try:
        r_lat = request_data['latitude']
        r_long = request_data['longitude']
    except KeyError as e:
        logging.error("Could not read request data:")
        logging.error(e)
        callback(None)

    nearest_squids = []

    ## computes the distance between each squid and the given ip address
    ## and sorts them in a list of squids
    for squid in shoal.values():
        s_lat = float(squid['geo_data']['latitude'])
        s_long = float(squid['geo_data']['longitude'])

        distance = haversine(r_lat, r_long, s_lat, s_long)

        nearest_squids.append((squid, distance))
    callback(nearest_squids)


@gen.engine
def get_nearest_squids(shoal, db_path, ip, count=10, callback=None):
    """
        Given an IP return a sorted list of nearest squids up to a given count
    """
    nearest_squids = yield gen.Task(calculate_distance, db_path, ip, shoal)
    squids = sorted(nearest_squids, key=lambda k: (k[1], k[0]['load']))
    callback(squids[:int(count)])


def haversine(lat1,lon1,lat2,lon2):
    """
        Calculate distance between two points using Haversine Formula.
    """
    # radius of earth
    r = 6371

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    return round((r * c),2)

def check_geolitecity_need_update(db_path, db_update):
    """
        Checks if the geolite database is outdated
    """
    curr = time()

    if os.path.exists(db_path):
        if curr - os.path.getmtime(db_path) < db_update:
            logging.info('GeoLiteCity is up-to-date')
            return False
        else:
            logging.warning('GeoLiteCity database needs updating.')
            return True
    else:
        logging.warning('GeoLiteCity database needs updating.')
        return True

def download_geolitecity(db_url, db_path, db_update):
    """
        Downloads a new geolite database
    """
    try:
        urlretrieve(db_url, db_path + '.gz')
    except Exception as e:
        logging.error("Could not download the database. - {0}".format(e))
        sys.exit(1)
    try:
        content = gzip.open(db_path + '.gz').read()
    except Exception as e:
        logging.error("GeoLiteCity.dat file was not properly downloaded. Check contents of {0} for possible errors.".format(db_path + '.gz'))
        sys.exit(1)

    with open(db_path,'w') as f:
        f.write(content)

    if check_geolitecity_need_update(db_url, db_update):
        logging.error('GeoLiteCity database failed to update.')

def generate_wpad(shoal, ip):
    """
        Parses the JSON of nearest squids and provides the data as a wpad
    """
    squids = get_nearest_squids(ip, shoal)
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
