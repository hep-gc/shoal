from os.path import join, expanduser, exists, abspath
import sys
import ConfigParser

# Shoal Options Module
"""Setup shoal using config file.
   setup will look for a configuration file specified in the following order:
     directory of shoal-server
     /etc/shoal/shoal_server.conf
     ~/.shoal/shoal_server.conf
   The first one found will be used.
"""
# set default values
shoal_dir = '/var/shoal/'
geolitecity_path = shoal_dir
geolitecity_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
geolitecity_update = 2592000
squid_cleanse_interval = 15
squid_inactive_time = 180
amqp_server_url = 'localhost'
amqp_port       = 5672
amqp_virtual_host = '/'
amqp_exchange = 'shoal'
amqp_exchange_type = 'topic'
use_ssl = False
amqp_ca_cert     = ''
amqp_client_cert = ''
amqp_client_key  = ''
webpy_cache = False
log_file = '/var/log/shoal_server.log'
error_reconnect_time = 30
error_reconnect_attempts = 10

homedir = expanduser('~')

#radius of earth used to calculate distnace vs load cost after haversine and a tuneable constant for the same calculation
earthradius = 6378
loadconstant = 1

#servers and repos to check for authentication
#These servers and repos will have to be updated once the occurences of /opt/ are removed
servers=["http://cvmfs.racf.bnl.gov:8000","http://cvmfs.fnal.gov:8000","http://cvmfs-stratum-one.cern.ch:8000","http://cernvmfs.gridpp.rl.ac.uk:8000","http://cvmfs02.grid.sinica.edu.tw:8000"]
#belle, nightlies should be in this list but every server is having trouble accessing it.
repos=["atlas","atlas-condb","sft","grid"]


# find config file by checking the directory of the calling script and sets path
if  exists(abspath(sys.path[0]+"/shoal_server.conf")):
    path = abspath(sys.path[0]+"/shoal_server.conf")
elif exists("/etc/shoal/shoal_server.conf"):
    path = "/etc/shoal/shoal_server.conf"
elif exists(abspath(homedir + "/.shoal/shoal_server.conf")):
    path = abspath(homedir + "/.shoal/shoal_server.conf")
else:
    print >> sys.stderr, "Configuration file problem: There doesn't " \
                         "seem to be a configuration file. " \
                         "You can specify one in /etc/shoal/shoal_server.conf"
    sys.exit(1)

# Read config file from the given path above
config_file = ConfigParser.ConfigParser()
try:
    config_file.read(path)
except IOError:
    print >> sys.stderr, "Configuration file problem: There was a " \
                         "problem reading %s. Check that it is readable," \
                         "and that it exists. " % path
    raise
except ConfigParser.ParsingError:
    print >> sys.stderr, "Configuration file problem: Couldn't " \
                         "parse your file. Check for spaces before or after variables."
    raise
except:
    print "Configuration file problem: There is something wrong with " \
          "your config file."
    raise

# sets defaults to the options in the config_file
if config_file.has_option("general", "shoal_dir"):
    shoal_dir = config_file.get("general", "shoal_dir")

if not config_file.has_option("general", "geolitecity_path"):
    geolitecity_path = shoal_dir
else:
    geolitecity_path = config_file.get("general", "geolitecity_path")

if config_file.has_option("general", "geolitecity_url"):
    geolitecity_url = config_file.get("general", "geolitecity_url")

if config_file.has_option("general", "geolitecity_update"):
    try:
        geolitecity_update = config_file.getint("general", "geolitecity_update")
    except ValueError:
        print "Configuration file problem: geolitecity_update must be an " \
              "integer value."
        sys.exit(1)

if config_file.has_option("squid", "squid_cleanse_interval"):
    try:
        squid_cleanse_interval = config_file.getint("squid", "squid_cleanse_interval")
    except ValueError:
        print "Configuration file problem: squid_cleanse_interval must be an " \
              "integer value."
        sys.exit(1)

if config_file.has_option("squid", "squid_inactive_time"):
    try:
        squid_inactive_time = config_file.getint("squid", "squid_inactive_time")
    except ValueError:
        print "Configuration file problem: squid_inactive_time must be an " \
              "integer value."
        sys.exit(1)

if config_file.has_option("rabbitmq", "amqp_server_url"):
    amqp_server_url = config_file.get("rabbitmq", "amqp_server_url")

if config_file.has_option("rabbitmq", "amqp_port"):
    try:
        amqp_port = config_file.getint("rabbitmq", "amqp_port")
    except ValueError:
        print "Configuration file problem: amqp_port must be an " \
              "integer value."
        sys.exit(1)

if config_file.has_option("rabbitmq", "amqp_virtual_host"):
    amqp_virtual_host = config_file.get("rabbitmq", "amqp_virtual_host")

if config_file.has_option("rabbitmq", "amqp_exchange"):
    amqp_exchange = config_file.get("rabbitmq", "amqp_exchange")

if config_file.has_option("rabbitmq", "amqp_exchange_type"):
    amqp_exchange_type = config_file.get("rabbitmq", "amqp_exchange_type")

if config_file.has_option("rabbitmq", "use_ssl") and config_file.getboolean("rabbitmq", "use_ssl"):
    try:
        use_ssl = True
        amqp_ca_cert     = abspath(config_file.get("rabbitmq", "amqp_ca_cert"))
        amqp_client_cert = abspath(config_file.get("rabbitmq", "amqp_client_cert"))
        amqp_client_key  = abspath(config_file.get("rabbitmq", "amqp_client_key"))
    except Exception as e:
        print "Configuration file problem: could not load SSL certs"
        print e
        sys.exit(1)

if config_file.has_option("webpy", "webpy_cache"):
    try:
        webpy_cache = config_file.getboolean("webpy", "webpy_cache")
    except ValueError:
        print "Configuration file problem: webpy_cache must be a " \
              "boolean value."
        sys.exit(1)

if config_file.has_option("logging", "log_file"):
    log_file = config_file.get("logging", "log_file")

if config_file.has_option("error", "error_reconnect_time"):
    try:
        error_reconnect_time = config_file.getint("error", "error_reconnect_time")
    except ValueError:
        print "Configuration file problem: error_reconnect_time must be an integer"

if config_file.has_option("error", "error_reconnect_attempts"):
    try:
        error_reconnect_attempts = config_file.getint("error", "error_reconnect_attempts")
    except ValueError:
        print "Configuration file problem: error_reconnect_attempts must be an integer"
