import sys
import os
import subprocess
import logging
import tarfile
import re
from time import time
from math import radians, cos, sin, asin, sqrt
from urllib.request import urlretrieve

import requests
import pygeoip
import geoip2.database
import shoal_server.sqlgeoip as sqlgeoip
import web

import socket
import copy

import shoal_server.config as config

GEOLITE_DB = os.path.join(config.geolitecity_path, "GeoLiteCity.mmdb")
GEOLITE_URL = config.geolitecity_url
GEOLITE_UPDATE = config.geolitecity_update

SQL_DB =  "geoip"

logger = logging.getLogger('shoal_server')
logger.setLevel(config.logging_level)
logging.getLogger("requests").setLevel(logging.WARNING)

def get_geolocation(ip):
    """
        Given an IP return all its geographical information (using GeoLiteCity.dat)
    """
    """  OLD .DAT IMPLEMENTATION
    try:
        gi = pygeoip.GeoIP(GEOLITE_DB)
        return gi.record_by_addr(ip)
    except Exception as exc:
        logger.error(exc)
        return None
    """
    """  OLD MMDB IMPLEMENTATION
    try:
        reader = geoip2.database.Reader(GEOLITE_DB)
        return reader.city(ip)
    except Exception as exc:
        logger.exception(exc)
        return None
    """
    try:
        reader = sqlgeoip.Reader(SQL_DB)
        return reader.city(ip)
    except Exception as exc:
        logger.exception(exc)
        return None

def get_nearest_squids(ip, count=10):
    """
        Previously this function returned list of all squids ranked by geographical distance.
        It makes sence that the returned list should always be of verified or same domain squids.
        For this reason, this function now simply calls  get_nearest_verified_squids.
    """
    return get_nearest_verified_squids(ip, count)

def get_nearest_verified_squids(ip, count=10):
    """
        Given an IP return a sorted list of nearest squids up to a given count
        Takes into account the special cases where a squid cannot be verified
        and will check the domain of the requester to see if it matches and if
        it does it will serve it to the requester
    """
    request_data = get_geolocation(ip)
    if not request_data:
        logger.debug("No geolocation for %s", str(ip))
        return None

    try:
        r_lat = request_data.location.latitude
        r_long = request_data.location.longitude
    except KeyError as exc:
        logger.error("Could not read request data:")
        logger.error(exc)
        return None

    nearest_squids = []

    # computes the distance between each squid and the given ip address
    # and sorts them in a list of squids based on distance vs load correlation

    earthrad = config.earthradius
    b = config.squid_loadconstant
    w = config.squid_distloadweight
    maxload = -1
    squid_key_list = list(web.shoal)
    for squid_key in squid_key_list:
        squid = web.shoal[squid_key]
        try:
            maxload = squid.maxload
        except:
            #no maxload is sent from agent, using default value
            maxload = config.squid_max_load

        # check if squid is verified or if verification is turned off in the config. or
        # if there is no global access but the requester is from the same domain
        same_domain = checkDomain(ip, squid.public_ip)
        if ((squid.verified or not config.squid_verification) and squid.global_access) or same_domain:

            s_lat = float(squid.geo_data.location.latitude)
            s_long = float(squid.geo_data.location.longitude)

            distance = haversine(r_lat, r_long, s_lat, s_long)
            distancecost = distance/(earthrad * 3.14159265359) * (w)
            loadcost = ((squid.load/maxload)**b) * (1-w)
            new_squid = copy.deepcopy(squid)
            if same_domain: 
                new_squid.local = True
            nearest_squids.append((new_squid, distancecost+loadcost))

    squids = sorted(nearest_squids, key=lambda k: (k[1]))
    return squids[:count]

def get_all_squids():
    """
        Return a list of all active squids
    """
    squids = []

    squid_key_list = list(web.shoal)
    for squid_key in squid_key_list:
        squid = web.shoal[squid_key]
        squids.append(squid)

    return squids

def lookupDomain(temp_ip):
    try:
        findDomain = subprocess.Popen('dig +nocomments  -x' + temp_ip + 'soa', shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        result = findDomain.communicate()[0].decode('utf-8').splitlines()
        for entry in result:
            if entry != '' and not entry.startswith(';'):
                return entry.split()[5]
        return None
    except Exception as exc:
        logger.error(exc)
        logger.error("Could not get the domain of ip %s", temp_ip)
        return None 

def checkDomain(req_ip, squid_ip):
    """
    Check if two ips come from the same domain
    """
    try:
        req_domain = lookupDomain(req_ip)
        squid_domain = lookupDomain(squid_ip)
        if (req_domain == squid_domain) and squid_domain is not None:
            return True
        else:
            return False
    except Exception as exc:
        logger.error(exc)
        logger.error("Could not compare the domain for the request ip %s and squid ip %s", req_ip, squid_ip)
        return False


def haversine(lat1, lon1, lat2, lon2):
    """
        Calculate distance between two points using Haversine Formula.
    """
    # radius of earth
    r = 6378

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    return round((r * c), 2)

def check_geolitecity_need_update():
    """
        Checks if the geolite database is outdated
    """
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

def generate_wpad(ip):
    """
        Parses the JSON of nearest squids and provides the data as a wpad
    """
    squids = get_nearest_squids(ip)
    if squids:
        proxy_str = ''
        for squid in squids:
            try:
                proxy_str += "PROXY http://{0}:{1};".format(squid[0].hostname, squid[0].squid_port)
            except TypeError:
                continue
        return proxy_str
    else:
        return None

def verify(squid):
    """
    This function is peridoically run by a daemon thread to
    reverify that the squids in shoal are active
    """

    # only verify if it is gobally accessable
    try:
        if squid.allow_verification:

            if not _is_available(squid):
                logger.warning("Failed Verification: %s ", str(squid.public_ip or squid.private_ip))
                squid.verified = False
                squid.allow_verification = False
            else:
                logger.info("VERIFIED:%s ", str(squid.public_ip or squid.private_ip))
                logger.warning("Got Verification: %s ", str(squid.public_ip or squid.private_ip))
                squid.verified = True
                squid.global_access = True
    except TypeError:
        logger.info("VERIFIED: %s", str(squid.public_ip or squid.private_ip))
        squid.verified = True

def _is_available(squid):
    """
    Downloads file thru proxy and assert its correctness to verify a given proxy
    A list of paths are tested to see all repos are working, the list can be found in
    config.py as "paths" returns the True if it is verified or False if it cannot be
    """
    ip = str(squid.public_ip or squid.private_ip)
    port = str(squid.squid_port)
    hostname = squid.hostname

    paths = config.paths
    proxystring = "http://%s:%s" % (ip, port)
    #set proxy
    proxies = {
        "http":proxystring,
    }
    badpaths = 0
    badflags = 0
    # test the ip with all the urls
    for targeturl in paths:
        #if a url checks out testflag set to true, otherwise fails verification at end of loop
        testflag = False
        if badpaths < 4 and badflags < 4:
            try:
                logger.info("Trying %s", targeturl)
                repo = re.search("cvmfs\/(.+?)(\/|\.)|opt\/(.+?)(\/|\.)", targeturl).group(1)
                if repo is None:
                    repo = re.search("cvmfs\/(.+?)(\/|\.)|opt\/(.+?)(\/|\.)", targeturl).group(3)
                file = requests.get(targeturl, proxies=proxies, timeout=2)
                f = file.content
                for line in f.splitlines():
                    if line.startswith(bytes('N', 'utf-8')):
                        if bytes(repo, 'utf-8') in line:
                            testflag = True
                    if bytes('ERR_ACCESS_DENIED', 'utf-8') in line:
                        squid.error = "The squid is configured to prevent external access. Squid is configured for Local Access Only. Cannot verify %s" % (hostname)
                        logger.error(squid.error)
                        return False
                if testflag is False:
                    badflags = badflags + 1
                    logger.error(
                        "%s failed verification on: %s. Currently %s out of %s IPs failing",
                        ip, targeturl, badflags, len(paths))
            except:
                # note that this would catch any RE errors aswell but they are
                # specified in the config and all fit the pattern.
                badpaths = badpaths + 1
                #logging.error(sys.exc_info()[1])
                logger.error("Timeout or proxy error on %s repo. Currently %s out of %s repos failing on testing %s", targeturl, badpaths, len(paths), ip)
            finally:
                #Keep going
                logger.debug("Next...")
        else:
            squid.error = "The squid firewall blocks the external access. Squid is configured for Local Access Only. Cannot verify %s" % (hostname)
            logger.error("%s repos failing, squid failed on verification. Squid is configured for Local Access Only. Cannot verify %s", badpaths, hostname)
            return False

    if badpaths < len(paths) and badflags < len(paths):
        #if all the IP is able to connect to the test URLs, return True
        return True
    else:
        squid.error = "%s/%s URLs have proxy errors and %s/%s URLs are unreachable. Squid is configured for Local Access Only. Cannot verify %s" % (badpaths, len(paths), badflags, len(paths), hostname)
        logger.error(squid.error)
        return False        
