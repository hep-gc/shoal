import urllib2
from urllib2 import urlopen
import json
import glob
import sys
import requests
import logging
import config

def is_available(ip, port):
    """
    using no system commands to download file thru proxy and assert its correctness to authenticate a given proxy
    returns the ip if it cannot authenticate it
    """
    servers = config.servers
    repos = config.repos
    proxystring = "http://%s:%s" % (ip,  str(port))
    #set proxy
    proxies = {
        "http":proxystring,
    }
    targeturl = ''
    for server in servers:
        for repo in repos:
            #this will need to be refactored with the changes to cvmfs
            if repo=='atlas' or 'atlas-condb':
                targeturl = "%s/opt/%s/.cvmfswhitelist" % (server, repo)
            else:
                targeturl = "%s/cvmfs/%s/.cvmfswhitelist" % (server, repo)

            try:
                file = requests.get(targeturl, proxies=proxies)
                f = file.content
            except:
                logging.info("Timeout or proxy error, blacklisting:%s " % (ip))
                return False
			
            for line in f.splitlines():
                if line.startswith('N'):
                    if repo in line:
                        return True
    return False

def authenticate(file, repo):
    """
    authenticate takes the file retrieved from a proxy and checks its conents
    for text that should be in the file, namely the name of the repo it was
    extracted from. If it finds the expected value it returns True, else it
    returns false and the given squid gets blacklisted.
    """
    with open(file, "r") as authfile:
        for line in authfile:
            if line.startswith('N'):
                if repo in line:
                    return True	

    return False 
