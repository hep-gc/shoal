import pygeoip, math
import web
import datetime
import time
import subprocess
import os

DB_PATH = '/home/mchester/shoal/shoal/GeoLiteCity.dat'

def get_geolocation(ip):
    diff = datetime.datetime.now() - datetime.timedelta(7)
    diff = time.mktime(diff.timetuple())
    if not os.path.isfile(DB_PATH):
        print "Database does not exist"

    gi = pygeoip.GeoIP(DB_PATH)
    web.debug(ip)
    return gi.record_by_addr(ip)

def get_nearest_squid(ip):
    web.debug('looking for squid')
    web.debug(ip)
    request_data = get_geolocation(ip)
    r_lat = request_data['latitude']
    r_long = request_data['longitude']

    smallest_distance = float("inf")
    nearest_squid = None

    for squid in web.shoal.values():
        s_lat = float(squid.data['latitude'])
        s_long = float(squid.data['longitude'])

        distance = get_distance_between_nodes(r_lat,r_long,s_lat,s_long)
        web.debug(distance)
        if distance < smallest_distance:
            smallest_distance = distance
            nearest_squid = squid
    web.debug(nearest_squid)
    return nearest_squid

# haversine forumla
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

def deg_to_rad(deg):
    return deg * (math.pi/180)
