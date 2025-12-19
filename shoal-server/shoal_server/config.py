from os.path import join, exists, abspath
import sys
import configparser

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
geodomain_path = "/var/www/shoal/static/db/"
geolitecity_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
geolitecity_update = 2592000
cache_cleanse_interval = 15
cache_inactive_time = 180
cache_verification = True
cache_verify_interval = 60
cache_max_load = 122000
cache_verified_default = False
cache_loadconstant = 1
cache_distloadweight = 0.5
amqp_server_url = 'localhost'
amqp_port       = 5672
amqp_virtual_host = '/'
amqp_exchange = 'shoal'
amqp_exchange_type = 'topic'
use_credentials = False
amqp_username = ''
amqp_password = ''
use_ssl = False
amqp_ca_cert     = ''
amqp_client_cert = ''
amqp_client_key  = ''
webpy_cache = False
log_file = '/var/log/shoal_server.log'
logging_level = 'WARNING'
error_reconnect_time = 30
error_reconnect_attempts = 10

#radius of earth used to calculate distnace vs load cost after haversine and a tuneable constant for the same calculation
earthradius = 6378


#servers and repos to check for authentication
paths = [
"http://cvmfs-stratum-one.cern.ch/cvmfs/atlas.cern.ch/.cvmfswhitelist",        
"http://cvmfs-stratum-one.cern.ch/cvmfs/atlas-condb.cern.ch/.cvmfswhitelist",      
"http://cvmfs-stratum-one.cern.ch/cvmfs/sft.cern.ch/.cvmfswhitelist",      
"http://cvmfs-stratum-one.cern.ch/cvmfs/grid.cern.ch/.cvmfswhitelist",
"http://cernvmfs.gridpp.rl.ac.uk/cvmfs/atlas.cern.ch/.cvmfswhitelist",
"http://cernvmfs.gridpp.rl.ac.uk/cvmfs/atlas-condb.cern.ch/.cvmfswhitelist",
"http://cernvmfs.gridpp.rl.ac.uk/cvmfs/sft.cern.ch/.cvmfswhitelist",
"http://cernvmfs.gridpp.rl.ac.uk/cvmfs/grid.cern.ch/.cvmfswhitelist",
"http://cvmfs.racf.bnl.gov/cvmfs/atlas.cern.ch/.cvmfswhitelist",
"http://cvmfs.racf.bnl.gov/cvmfs/atlas-condb.cern.ch/.cvmfswhitelist",
"http://cvmfs.racf.bnl.gov/cvmfs/sft.cern.ch/.cvmfswhitelist",
"http://cvmfs.racf.bnl.gov/cvmfs/grid.cern.ch/.cvmfswhitelist",
"http://cvmfs.fnal.gov/cvmfs/atlas.cern.ch/.cvmfswhitelist",
"http://cvmfs.fnal.gov/cvmfs/atlas-condb.cern.ch/.cvmfswhitelist",
"http://cvmfs.fnal.gov/cvmfs/sft.cern.ch/.cvmfswhitelist",
"http://cvmfs.fnal.gov/cvmfs/grid.cern.ch/.cvmfswhitelist"
]

# find config file by checking the directory of the calling script and sets path
if exists("/etc/shoal/shoal_server.conf"):
    path = "/etc/shoal/shoal_server.conf"
else:
    print ("Configuration file problem: There doesn't " \
           "seem to be a configuration file. " \
           "You can specify one in /etc/shoal/shoal_server.conf", file=sys.stderr)
    sys.exit(1)

# Read config file from the given path above
config_file = configparser.ConfigParser()
try:
    config_file.read(path)
except IOError:
    print ("Configuration file problem: There was a " \
           "problem reading %s. Check that it is readable," \
           "and that it exists. " % path , file=sys.stderr)
    raise
except configparser.ParsingError:
    print ("Configuration file problem: Couldn't " \
           "parse your file. Check for spaces before or after variables.", file=sys.stderr)
    raise
except:
    print ("Configuration file problem: There is something wrong with " \
           "your config file.")
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
    
if config_file.has_option("general", "geodomain_path"):
    geodomain_path = config_file.get("general", "geodomain_path")

if config_file.has_option("general", "geolitecity_update"):
    try:
        geolitecity_update = config_file.getint("general", "geolitecity_update")
    except ValueError:
        print ("Configuration file problem: geolitecity_update must be an " \
               "integer value.")
        sys.exit(1)

if config_file.has_option("cache", "cache_cleanse_interval"):
    try:
        cache_cleanse_interval = config_file.getint("cache", "cache_cleanse_interval")
    except ValueError:
        print ("Configuration file problem: cache_cleanse_interval must be an " \
               "integer value.")
        sys.exit(1)

if config_file.has_option("cache", "cache_inactive_time"):
    try:
        cache_inactive_time = config_file.getint("cache", "cache_inactive_time")
    except ValueError:
        print ("Configuration file problem: cache_inactive_time must be an " \
               "integer value.")
        sys.exit(1)
        
if config_file.has_option("cache", "cache_verification"):
    try:
        cache_verification = config_file.getboolean("cache", "cache_verification")
    except ValueError:
        print ("Configuration file problem: cache_verification must be a boolean value")
        sys.exit(1)

if config_file.has_option("cache", "cache_verified_default"):
    try:
        cache_verified_default = config_file.getboolean("cache", "cache_verified_default")
    except ValueError:
        print ("Configuration file problem: cache_verified_default must be a boolean value")
        sys.exit(1)

if config_file.has_option("cache", "cache_verify_interval"):
    try:
        cache_verify_interval = config_file.getint("cache", "cache_verify_interval")
    except ValueError:
        print ("Configuration file problem: cache_verify_interval must be a integer value")
        sys.exit(1)

if config_file.has_option("cache", "cache_max_load"):
    try:
        cache_max_load = config_file.getint("cache", "cache_max_load")
    except ValueError:
        print ("Configuration file problem: cache_max_load must be a integer value")
        sys.exit(1)

if config_file.has_option("cache", "cache_loadconstant"):
    try:
        cache_loadconstant = config_file.getfloat("cache", "cache_loadconstant")
    except ValueError:
        print ("Configuration file problem: cache_loadconstant must be a float value")
        sys.exit(1)

if config_file.has_option("cache", "cache_distloadweight"):
    try:
        cache_distloadweight = config_file.getfloat("cache", "cache_distloadweight")
    except ValueError:
        print ("Configuration file problem: cache_distloadweight must be a float value")
        sys.exit(1)

if config_file.has_option("rabbitmq", "amqp_server_url"):
    amqp_server_url = config_file.get("rabbitmq", "amqp_server_url")

if config_file.has_option("rabbitmq", "amqp_port"):
    try:
        amqp_port = config_file.getint("rabbitmq", "amqp_port")
    except ValueError:
        print ("Configuration file problem: amqp_port must be an " \
               "integer value.")
        sys.exit(1)

if config_file.has_option("rabbitmq", "amqp_virtual_host"):
    amqp_virtual_host = config_file.get("rabbitmq", "amqp_virtual_host")

if config_file.has_option("rabbitmq", "amqp_exchange"):
    amqp_exchange = config_file.get("rabbitmq", "amqp_exchange")

if config_file.has_option("rabbitmq", "amqp_exchange_type"):
    amqp_exchange_type = config_file.get("rabbitmq", "amqp_exchange_type")
    
if config_file.has_option("rabbitmq", "use_credentials") and config_file.getboolean("rabbitmq", "use_credentials"):
    use_credentials = True
    amqp_username = config_file.get("rabbitmq", "amqp_username")
    amqp_password = config_file.get("rabbitmq", "amqp_password")

if config_file.has_option("rabbitmq", "use_ssl") and config_file.getboolean("rabbitmq", "use_ssl"):
    try:
        use_ssl = True
        amqp_ca_cert     = abspath(config_file.get("rabbitmq", "amqp_ca_cert"))
        amqp_client_cert = abspath(config_file.get("rabbitmq", "amqp_client_cert"))
        amqp_client_key  = abspath(config_file.get("rabbitmq", "amqp_client_key"))
    except Exception as e:
        print ("Configuration file problem: could not load SSL certs")
        print (e)
        sys.exit(1)

if config_file.has_option("webpy", "webpy_cache"):
    try:
        webpy_cache = config_file.getboolean("webpy", "webpy_cache")
    except ValueError:
        print ("Configuration file problem: webpy_cache must be a " \
              "boolean value.")
        sys.exit(1)

if config_file.has_option("logging", "log_file"):
    log_file = config_file.get("logging", "log_file")

if config_file.has_option("logging", "logging_level"):
    logging_level = config_file.get("logging", "logging_level")

if config_file.has_option("error", "error_reconnect_time"):
    try:
        error_reconnect_time = config_file.getint("error", "error_reconnect_time")
    except ValueError:
        print ("Configuration file problem: error_reconnect_time must be an integer")

if config_file.has_option("error", "error_reconnect_attempts"):
    try:
        error_reconnect_attempts = config_file.getint("error", "error_reconnect_attempts")
    except ValueError:
        print ("Configuration file problem: error_reconnect_attempts must be an integer")
