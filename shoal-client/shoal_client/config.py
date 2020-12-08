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
default_squid_proxy   = ""

homedir = expanduser('~')
# find config file by checking the directory of the calling script and sets path
if  exists(abspath(sys.path[0]+"/shoal_client.conf")):
    path = abspath(sys.path[0]+"/shoal_client.conf")
elif exists("/etc/shoal/shoal_client.conf"):
    path = "/etc/shoal/shoal_client.conf"
elif exists(abspath(homedir + "/.shoal/shoal_client.conf")):
    path =  abspath(homedir + "/.shoal/shoal_client.conf")
else:
    print >> sys.stderr, "Configuration file problem: There doesn't " \
                         "seem to be a configuration file. " \
                         "You can specify one in /etc/shoal/shoal_client.conf"
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
          "your config file.")
    raise

# sets defaults to the options in config_file
if config_file.has_option("general", "shoal_server_url"):
    shoal_server_url = config_file.get("general", "shoal_server_url")

if config_file.has_option("general", "default_squid_proxy"):
    default_squid_proxy = config_file.get("general", "default_squid_proxy")
else:
    print("Configuration file problem: default_squid_proxy must be set. " \
          "Please check configuration file:", path)
    sys.exit(1)

