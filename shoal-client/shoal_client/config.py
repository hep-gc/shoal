from __future__ import print_function
from os.path import exists, join, expanduser, abspath, realpath
import sys
try:
    import configparser
except:
    import ConfigParser as configparser
import logging

# Shoal Options Module

"""Setup shoal using config file.
   setup will look for a configuration file specified in the following order:
     directory of shoal-client
     /etc/shoal/shoal_client.conf
     ~/.shoal/shoal_client.conf
   The first one found will be used.
"""
# set default values
shoal_server_url = 'http://localhost:8080/nearest'
default_squid_proxy = "DIRECT"
paths = [
"http://cvmfs-stratum-one.cern.ch/cvmfs/atlas-condb.cern.ch/.cvmfswhitelist",
"http://cernvmfs.gridpp.rl.ac.uk/cvmfs/sft.cern.ch/.cvmfswhitelist",
"http://cvmfs.racf.bnl.gov/cvmfs/atlas.cern.ch/.cvmfswhitelist",
"http://cvmfs.fnal.gov/cvmfs/grid.cern.ch/.cvmfswhitelist"
]

# get default http proxy from cvmfs config file
try:
    with open('/etc/cvmfs/default.local') as f:
        for line in f:
            info = line.split('=')
            if info[0] == 'CVMFS_HTTP_PROXY' and info[1]:
                cvmfs_proxies = info[1].strip()
                if cvmfs_proxies.startswith('"'):
                    cvmfs_proxies = cvmfs_proxies[1:]
                if cvmfs_proxies.endswith('"'):
                    cvmfs_proxies = cvmfs_proxies[:-1]
                each_proxies = cvmfs_proxies.split(';')
                for proxy in each_proxies:
                    if proxy not in default_squid_proxy: 
                        default_squid_proxy = proxy + ';' + default_squid_proxy 
except:
    print("No default cvmfs http proxy found", file=sys.stderr)

homedir = expanduser('~')
# find config file by checking the directory of the calling script and sets path
if  exists(abspath(sys.path[0]+"/shoal_client.conf")):
    path = abspath(sys.path[0]+"/shoal_client.conf")
elif exists(abspath(homedir + "/.shoal/shoal_client.conf")):
    path =  abspath(homedir + "/.shoal/shoal_client.conf")
elif exists("/etc/shoal/shoal_client.conf"):
    path = "/etc/shoal/shoal_client.conf"
else:
    print("Configuration file problem: There doesn't " \
                         "seem to be a configuration file. " \
                         "You can specify one in /etc/shoal/shoal_client.conf", file=sys.stderr)
    sys.exit(1)

# Read config file from the given path above
config_file = configparser.ConfigParser()
try:
    config_file.read(path)
except IOError:
    print("Configuration file problem: There was a " \
                         "problem reading %s. Check that it is readable," \
                         "and that it exists. " % path, file=sys.stderr)
    raise
except configparser.ParsingError:
    print("Configuration file problem: Couldn't " \
                         "parse your file. Check for spaces before or after variables.", file=sys.stderr)
    raise
except:
    print("Configuration file problem: There is something wrong with " \
          "your config file.", file=sys.stderr)
    raise

# sets defaults to the options in config_file
if config_file.has_option("general", "shoal_server_url"):
    shoal_server_url = config_file.get("general", "shoal_server_url")

if config_file.has_option("general", "default_squid_proxy"):
    default_squid_proxy = config_file.get("general", "default_squid_proxy")
else:
    print("No default settings found in the config file, will use DIRECT as default. " \
          "Please check configuration file: %s" % path, file=sys.stderr)

