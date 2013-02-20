import sys
import os
import subprocess
import pygeoip, math
import web
import config
from time import time, sleep

"""
    Given an IP return all its geographical information (using GeoLiteCity.dat)
"""
def get_geolocation(ip):
    geolitecity_path = config.geolitecity_path

    gi = pygeoip.GeoIP(geolitecity_path)
    return gi.record_by_addr(ip)

"""
    Given an IP return IP of nearest squid.
"""
def get_nearest_squid(ip):
    request_data = get_geolocation(ip)
    r_lat = request_data['latitude']
    r_long = request_data['longitude']

    smallest_distance = float("inf")
    nearest_squid = None

    for squid in web.shoal.values():
        s_lat = float(squid.geo_data['latitude'])
        s_long = float(squid.geo_data['longitude'])

        distance = get_distance_between_nodes(r_lat,r_long,s_lat,s_long)

        if distance < smallest_distance:
            smallest_distance = distance
            nearest_squid = squid

    return nearest_squid

"""
    Calculate distance between two points using Haversine Formula.
"""
def get_distance_between_nodes(lat1,long1,lat2,long2):
    # radius of earth
    r = 6371
    d_lat = deg_to_rad(lat2-lat1)
    d_long = deg_to_rad(long2-long1)

    a = math.sin(d_lat/2) * math.sin(d_lat/2) + \
        math.cos(deg_to_rad(lat1)) * math.cos(deg_to_rad(lat2)) * \
        math.sin(d_long/2) * math.sin(d_long/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = r * c
    return d

"""
    Helper functions
"""
def deg_to_rad(deg):
    return deg * (math.pi/180)

def check_geolitecity():
    curr = time()
    geolitecity_update = config.geolitecity_update
    geolitecity_path = config.geolitecity_path

    if os.path.exists(geolitecity_path):
        if os.path.getmtime(geolitecity_path) - curr > geolitecity_update:
            return True
        else:
            return False
    else:
        return True

def download_geolitecity():
    geolitecity_path = config.geolitecity_path
    cmd = ['wget',config.geolitecity_url]

    ungz = ['gunzip','{0}.gz'.format(geolitecity_path)]
    try:
        dl = subprocess.Popen(cmd)
        dl.wait()
        sleep(2)
        gz = subprocess.Popen(ungz)
        gz.wait()

    except Exception as e:
        print "Could not download the database. - {0}".format(e)
        sys.exit(1)
