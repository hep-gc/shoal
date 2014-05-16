import urllib2
from urllib2 import urlopen
import json
import os
import glob
import sys
import requests
import logging
import config

"""
parseServerData parses the JSON data to get the squid ports and ip of the squid cashes,
for each ip it finds it tries to run an authentication test and if the test fails the 
IP is added to a blacklist which is then returned up the call tree.
"""
def parseServerData(jsonStr):
    try:
        data = json.loads(jsonStr)
    except JSONException:
        logging.info("Json exception, invalid json dump.")
        return Null
    except ValueError:
        logging.info("JSON string value error, invalid json dump.")
        return Null

    ips = []
    ports = []
    blacklist = []
    verifications = []
    i = 0

    if data!=None:
        for x in data:
            ips.append(data[x]['public_ip'])
            ports.append(data[x]['squid_port'])
            verifications.append(data[x]['verification'])
            if 'verified' in verifications[i]:
                blacklist.append(authTest(ips[i], ports[i]))
            i = i+1
    return blacklist

#using no system commands to download file thru proxy and assert its correctness to authenticate a given proxy
def authTest(ip, port):

    blacklist = []		
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
            #this is broken and will need to be fixed. everything defaulting to /opt/ for now
            if repo=='atlas' or 'atlas-condb':
                targeturl = "%s/opt/%s/.cvmfswhitelist" % (server, repo)
            else:
                targeturl = "%s/cvmfs/%s/.cvmfswhitelist" % (server, repo)

            try:
                file = requests.get(targeturl, proxies=proxies)
                f = file.content
            except:
                logging.info("Timeout or proxy error, blacklisting:%s " % (ip))
                blacklist.append(ip)
                return blacklist
			
            #variable to check before adding ip to blacklist
            blist = True
            for line in f.splitlines():
                if line.startswith('N'):
                    if repo in line:
                        blist = False
                        break     
            if blist:
                blacklist.append(ip)
                return blacklist

"""
authenticate takes the file retrieved from a proxy and checks its conents
for text that should be in the file, namely the name of the repo it was
extracted from. If it finds the expected value it returns True, else it
returns false and the given squid gets blacklisted.
"""
def authenticate(file, repo):
    with open(file, "r") as authfile:
        for line in authfile:
            if line.startswith('N'):
                if repo in line:
                    return True	

    return False 

"""
cleanUp is a function implimented for the wget test. Since wget actually
downloads the file to the local system the files needed to be removed after.
With the wget test now obsolete this function is no longer needed.
"""
def cleanUp():
    for filename in glob.glob(".cvm*"):
        os.remove(filename)

"""
audit is the function that gets called externally, it takes a shoal server
as a parameter and retrives the JSON dump produced by the server and sends
it to parseServerData to do the heavy lifting and compiling of the blacklist.
"""
def audit(server):
    try:
        f = urlopen(server)
        blacklist = parseServerData(f.read())
        f.close()
        return blacklist

    except urllib2.HTTPError, e:
        logging.info("Problem connecting to: %s" % (server))
        return Null
    except urllib2.URLError, e:
        logging.info("Problem connecting to: %s" % (server))
        return Null
    except httplib.HTTPException, e:
        logging.info("Problem connecting to: %s" % (server))
        return Null
    except Exception:
        logging.info("Problem connecting to: %s" % (server))
        return Null

