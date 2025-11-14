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

def get_nearest_caches(ip, count=10, upstream_type=None):
    """
        Previously this function returned list of all caches ranked by geographical distance.
        It makes sence that the returned list should always be of verified or same domain caches.
        For this reason, this function now simply calls  get_nearest_verified_caches.
    """
    return get_nearest_verified_caches(ip, count,upstream_type)

def get_nearest_verified_caches(ip, count=10, upstream_type= None):
    """
        Given an IP return a sorted list of nearest caches up to a given count
        Takes into account the special cases where a cache cannot be verified
        and will check the domain of the requester to see if it matches and if
        it does it will serve it to the requester
    """
    upstream_list = [upstream_type, 'both']
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

    nearest_caches = []

    # computes the distance between each cache and the given ip address
    # and sorts them in a list of caches based on distance vs load correlation

    earthrad = config.earthradius
    b = config.cache_loadconstant
    w = config.cache_distloadweight
    maxload = -1
    cache_key_list = list(web.shoal)
    for cache_key in cache_key_list:
        cache = web.shoal[cache_key]

        if upstream_type is not None and cache.upstream.lower() not in upstream_list:
            continue
        
        
        try:
            maxload = cache.maxload
        except:
            #no maxload is sent from agent, using default value
            maxload = config.cache_max_load

        # check if cache is verified or if verification is turned off in the config. or
        # if there is no global access but the requester is from the same domain
        same_domain = checkDomain(ip, cache.public_ip)
        if ((cache.verified or not config.cache_verification) and cache.global_access) or same_domain:

            s_lat = float(cache.geo_data.location.latitude)
            s_long = float(cache.geo_data.location.longitude)

            distance = haversine(r_lat, r_long, s_lat, s_long)
            distancecost = distance/(earthrad * 3.14159265359) * (w)
            loadcost = ((cache.load/maxload)**b) * (1-w)
            new_cache = copy.deepcopy(cache)
            if same_domain: 
                new_cache.local = True
            nearest_caches.append((new_cache, distancecost+loadcost))

    caches = sorted(nearest_caches, key=lambda k: (k[1]))
    return caches[:count]

def get_all_caches():
    """
        Return a list of all active caches
    """
    caches = []

    cache_key_list = list(web.shoal)
    for cache_key in cache_key_list:
        cache = web.shoal[cache_key]
        caches.append(cache)

    return caches

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

def checkDomain(req_ip, cache_ip):
    """
    Check if two ips come from the same domain
    """
    try:
        req_domain = lookupDomain(req_ip)
        cache_domain = lookupDomain(cache_ip)
        if (req_domain == cache_domain) and cache_domain is not None:
            return True
        else:
            return False
    except Exception as exc:
        logger.error(exc)
        logger.error("Could not compare the domain for the request ip %s and cache ip %s", req_ip, cache_ip)
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
        Parses the JSON of nearest caches and provides the data as a wpad
    """
    caches = get_nearest_caches(ip)
    if caches:
        proxy_str = ''
        for cache in caches:
            try:
                proxy_str += "PROXY http://{0}:{1};".format(cache[0].hostname, cache[0].cache_port)
            except TypeError:
                continue
        return proxy_str
    else:
        return None

def verify(cache):
    """
    This function is peridoically run by a daemon thread to
    reverify that the caches in shoal are active
    """

    # only verify if it is gobally accessable
    try:
        if cache.allow_verification:

            if not _is_available(cache):
                logger.warning("Failed Verification: %s ", str(cache.public_ip or cache.private_ip))
                cache.verified = False
                cache.allow_verification = False
            else:
                logger.info("VERIFIED:%s ", str(cache.public_ip or cache.private_ip))
                logger.warning("Got Verification: %s ", str(cache.public_ip or cache.private_ip))
                cache.verified = True
                cache.global_access = True
    except TypeError:
        logger.info("VERIFIED: %s", str(cache.public_ip or cache.private_ip))
        cache.verified = True

def _is_available(cache):
    """
    Downloads file thru proxy and assert its correctness to verify a given proxy
    A list of paths are tested to see all repos are working, the list can be found in
    config.py as "paths" returns the True if it is verified or False if it cannot be
    """
    ip = str(cache.public_ip or cache.private_ip)
    port = str(cache.cache_port)
    hostname = cache.hostname
    cache_type = cache.cache_type if hasattr(cache, 'cache_type') else 'cache'
    upstream = cache.upstream.lower() if hasattr(cache, 'upstream') else 'both'
    
    paths = config.paths
    proxystring = "http://%s:%s" % (ip, port)
    #set proxy
    proxies = {
        "http":proxystring,
    }
        
    try:
        if cache_type == 'varnish':
            if upstream == 'cvmfs':
                targeturl = "http://cvmfs-s1goc.opensciencegrid.org:8000/cvmfs/oasis.opensciencegrid.org/.cvmfspublished"
                repo = re.search("cvmfs\/(.+?)(\/|\.)|opt\/(.+?)(\/|\.)", targeturl).group(1)
                if repo is None:
                    repo = re.search("cvmfs\/(.+?)(\/|\.)|opt\/(.+?)(\/|\.)", targeturl).group(3)
                file = requests.get(targeturl, timeout=2)
                f = file.content
                for line in f.splitlines():
                    if line.startswith(bytes('N', 'utf-8')):
                        if bytes(repo, 'utf-8') in line:
                            return True
                logger.error("%s failed verification on %s" % (ip, targeturl))
                cache.error = "Varnish CVMFS cache failed verification"
                return False
            elif upstream == 'frontier':
                targeturl = proxystring + "/atlr"
                file = requests.get(targeturl, headers={"X-frontier-id": "shoal-server-verification", "Cache-Control": "max-age=0"}, timeout=2)
                if file.status_code == 200:
                    return True
                logger.error("%s failed verification on %s" % (ip, targeturl))
                cache.error = "Varnish Frontier cache failed verification. Status: %s" % file.status_code
                return False
        else:
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
                                cache.error = "The cache is configured to prevent external access. Cache is configured for Local Access Only. Cannot verify %s" % (hostname)
                                logger.error(cache.error)
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
                    cache.error = "The cache firewall blocks the external access. Cache is configured for Local Access Only. Cannot verify %s" % (hostname)
                    logger.error("%s repos failing, cache failed on verification. Cache is configured for Local Access Only. Cannot verify %s", badpaths, hostname)
                    return False
        
            if badpaths < len(paths) and badflags < len(paths):
                #if all the IP is able to connect to the test URLs, return True
                return True
            else:
                cache.error = "%s/%s URLs have proxy errors and %s/%s URLs are unreachable. Cache is configured for Local Access Only. Cannot verify %s" % (badpaths, len(paths), badflags, len(paths), hostname)
                logger.error(cache.error)
                return False  
                
    except Exception as exc:
        logger.error("%s timeout or error: %s" % (ip, str(exc)))
        cache.error = "Error during verification"
        return False
    
    return True






