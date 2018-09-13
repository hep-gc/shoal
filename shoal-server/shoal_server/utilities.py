import sys
import os
import logging
import gzip
import re
from time import time
from math import radians, cos, sin, asin, sqrt
from urllib import urlretrieve

import requests
import pygeoip
import geoip2.database
import web

import shoal_server.config as config

GEOLITE_DB = os.path.join(config.geolitecity_path, "GeoLiteCity.dat")
GEOLITE_URL = config.geolitecity_url
GEOLITE_UPDATE = config.geolitecity_update
GEODOMAIN_DB = os.path.join(config.geodomain_path, "GeoIP2-Domain.mmdb")

logger = logging.getLogger('shoal_server')
logging.getLogger("requests").setLevel(logging.WARNING)

def get_geolocation(ip):
    """
        Given an IP return all its geographical information (using GeoLiteCity.dat)
    """
    try:
        gi = pygeoip.GeoIP(GEOLITE_DB)
        return gi.record_by_addr(ip)
    except Exception as exc:
        logger.error(exc)
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
        print "no geolocation"
        return None

    try:
        r_lat = request_data['latitude']
        r_long = request_data['longitude']
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
    for squid in web.shoal.values():
        try:
            maxload = squid.maxload
        except:
            #no maxload is sent from agent, using default value
            maxload = config.squid_max_load

        # check if squid is verified or if verification is turned off in the config. or
        # if there is no global access but the requester is from the same domain
        if ((squid.verified or not config.squid_verification) and squid.global_access) or checkDomain(ip, squid.public_ip):

            s_lat = float(squid.geo_data['latitude'])
            s_long = float(squid.geo_data['longitude'])

            distance = haversine(r_lat, r_long, s_lat, s_long)
            distancecost = distance/(earthrad * 3.14159265359) * (w)
            loadcost = ((squid.load/maxload)**b) * (1-w)
            nearest_squids.append((squid, distancecost+loadcost))

    squids = sorted(nearest_squids, key=lambda k: (k[1]))
    return squids[:count]

def get_all_squids():
    """
        Return a list of all active squids
    """
    squids = []

    for squid in web.shoal.values():
        squids.append(squid)

    return squids

def checkDomain(req_ip, squid_ip):
    """
    Check if two ips come from the same domain
    If no database file is detected produce an error message and continue
    functioning without the domain lookup feature
    """
    if os.path.exists(GEODOMAIN_DB):
        try:
            reader = geoip2.database.Reader(GEODOMAIN_DB)
            req_domain = reader.domain(req_ip)
            squid_domain = reader.domain(squid_ip)
            if (req_domain.domain == squid_domain.domain) and squid_domain.domain is not None:
                return True
            else:
                return False
        except Exception as exc:
            logging.error(exc)
            logging.error("IP not found in database - could not find second level domain name")
            return False
    else:
        logging.error("No geoDomain database file detected. Add the database file "
                      "to shoal-server/static/db before installation and ensure the path in "
                      "the config file is correct")
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

def download_geolitecity():
    """
        Downloads a new geolite database
    """
    try:
        urlretrieve(GEOLITE_URL, GEOLITE_DB + '.gz')
    except Exception as exc:
        logger.error("Could not download the database. - %s", exc)
        sys.exit(1)
    try:
        content = gzip.open(GEOLITE_DB + '.gz').read()
    except Exception:
        logger.error("GeoLiteCity.dat file was not properly downloaded. "
                     "Check contents of %s for possible errors.", (GEOLITE_DB + '.gz'))
        sys.exit(1)

    try:
        with open(GEOLITE_DB, 'w') as f:
            f.write(content)
    except Exception as exc:
        logger.error("Unable to open Geolite city database for writing..")
        logger.error(exc)

    if check_geolitecity_need_update():
        logger.error('GeoLiteCity database failed to update.')

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
        if squid.global_access or squid.domain_access:

            if not _is_available(squid):
                logging.info("Failed Verification: %s ", str(squid.public_ip or squid.private_ip))
                squid.verified = False
            else:
                logging.info("VERIFIED:%s ", str(squid.public_ip or squid.private_ip))
                squid.verified = True
    except TypeError:
        logging.info("VERIFIED: %s", str(squid.public_ip or squid.private_ip))
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
    for targeturl in paths:
        #if a url checks out testflag set to true, otherwise fails verification at end of loop
        testflag = False
        try:
            logging.info("Trying %s", targeturl)
            repo = re.search("cvmfs\/(.+?)(\/|\.)|opt\/(.+?)(\/|\.)", targeturl).group(1)
            if repo is None:
                repo = re.search("cvmfs\/(.+?)(\/|\.)|opt\/(.+?)(\/|\.)", targeturl).group(3)
            file = requests.get(targeturl, proxies=proxies, timeout=2)
            f = file.content
            for line in f.splitlines():
                if line.startswith('N'):
                    if repo in line:
                        testflag = True
                        goodurl = targeturl
            if testflag is False:
                badflags = badflags + 1
                logging.error(
                    "%s failed verification on: %s. Currently %s out of %s IPs failing",
                    ip, targeturl, badflags, len(paths))
        except:
            # note that this would catch any RE errors aswell but they are
            # specified in the config and all fit the pattern.
            badpaths = badpaths + 1
            #logging.error(sys.exc_info()[1])
            logging.error(
                "Timeout or proxy error on %s repo. Currently %s out of %s repos failing",
                targeturl, badpaths, len(paths))
        finally:
            #Keep going
            logging.info("Next...")

    if badpaths < len(paths) and badflags < len(paths):
        #if all the IP is able to connect to the test URLs, then check the
        # actual squid URL to make sure both IP and URL are good.
        try:
            proxystring = "http://%s:%s" % (hostname, port)
            #set proxy
            proxy = {
                "http":proxystring,
            }
            file = requests.get(goodurl, proxies=proxy, timeout=2)
        except ConnectionError:
            squid.error = "DNS failure or refused connection."
            logging.error(squid.error)
            return False
        except HTTPError:
            squid.error = "Invalid HTTP response."
            logging.error(squid.error)
            return False
        except Timeout:
            squid.error = "Timeout out on: " + proxy
            logging.error(squid.error)
            return False
        except RquestException:
            squid.error = "DNS configuration error! Squid IP is OK, but squid URL is wrong."
            logging.error(squid.error)
            return False
        return True
    else:
        if squid.domain_access and squid.global_access:
            squid.error = "Configuration conflict detected! %s is configured " \
                          "for both Local Access Only and Global Access."  % (hostname)

        if squid.domain_access and not squid.global_access:
            squid.error = "Squid is configured for Local Access Only. Cannot verify %s" % (hostname)
        else:
            squid.error = "%s/%s URLs have proxy errors and %s/%s URLs are unreachable. %s has " \
                          "been blacklisted" % (badpaths, len(paths), badflags, len(paths), hostname)
        logging.error(squid.error)
        return False        
