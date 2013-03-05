"""
  Very simple client script used to get nearest squid server using the RESTful API.
"""

import urllib2
import sys
import json
import logging

from urllib2 import urlopen

url = 'http://elephant68.heprc.uvic.ca:8080/nearest'

try:
    f = urlopen(url)
except urllib2.URLError as e:
    logging.error("Unable to open url. %s" % e)
    sys.exit(1)

data = json.loads(f.read())

print 'Public IP:', data['public_ip']
print 'Private IP:', data['private_ip']
