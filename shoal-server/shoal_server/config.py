from os.path import join, expanduser, exists
import sys
import ConfigParser

# Shoal Options Module

# set default values
shoal_dir = '/var/shoal/'
geolitecity_path = shoal_dir
geolitecity_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
geolitecity_update = 2592000
squid_cleanse_interval = 15
squid_inactive_time = 180
amqp_server_url = 'amqp://guest:guest@localhost:5672'
amqp_virtual_host = '/'
amqp_exchange = 'shoal'
amqp_exchange_type = 'topic'
webpy_cache = False
log_file = '/var/log/shoal_server.log'
error_reconnect_time = 30
error_reconnect_attempts = 10

def setup(path=None):
    """Setup shoal using config file.
       setup will look for a configuration file specified in /etc/shoal/shoal_server.conf
    """
    global shoal_dir
    global geolitecity_path
    global geolitecity_url
    global geolitecity_update
    global squid_cleanse_interval
    global squid_inactive_time
    global amqp_server_url
    global amqp_virtual_host
    global amqp_exchange
    global amqp_exchange_type
    global webpy_cache
    global log_file   
    global error_reconnect_time 
    global error_reconnect_attempts 

    homedir = expanduser('~')

    # find config file
    if not path:
        if exists("/etc/shoal/shoal_server.conf"):
            path = "/etc/shoal/shoal_server.conf"
        elif exists(join(homedir, '.shoal/shoal_server.conf')):
            path = join(homedir, '.shoal/shoal_server.conf')
        else:
            print >> sys.stderr, "Configuration file problem: There doesn't " \
                  "seem to be a configuration file. " \
                  "You can specify one in /etc/shoal/shoal_server.conf"
            sys.exit(1)

    # Read config file
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

    if config_file.has_option("general", "shoal_dir"):
        shoal_dir = config_file.get("general",
                                       "shoal_dir")
        if not config_file.has_option("general", "geolitecity_path"):
            geolitecity_path = shoal_dir

    if config_file.has_option("general", "geolitecity_path"):
        geolitecity_path = config_file.get("general",
                                                "geolitecity_path")

    if config_file.has_option("general", "geolitecity_url"):
        geolitecity_url = config_file.get("general",
                                                "geolitecity_url")

    if config_file.has_option("general", "geolitecity_update"):
        try:
            geolitecity_update = config_file.getint("general",
                                                    "geolitecity_update")
        except ValueError:
            print "Configuration file problem: geolitecity_update must be an " \
                  "integer value."
            sys.exit(1)

    if config_file.has_option("squid", "squid_cleanse_interval"):
        try:
            squid_cleanse_interval = config_file.getint("squid",
                                                        "squid_cleanse_interval")
        except ValueError:
            print "Configuration file problem: squid_cleanse_interval must be an " \
                  "integer value."
            sys.exit(1)

    if config_file.has_option("squid", "squid_inactive_time"):
        try:
            squid_inactive_time = config_file.getint("squid",
                                                    "squid_inactive_time")
        except ValueError:
            print "Configuration file problem: squid_inactive_time must be an " \
                  "integer value."
            sys.exit(1)

    if config_file.has_option("rabbitmq", "amqp_server_url"):
        amqp_server_url = config_file.get("rabbitmq",
                                                "amqp_server_url")

    if config_file.has_option("rabbitmq", "amqp_virtual_host"):
        amqp_virtual_host = config_file.get("rabbitmq",
                                                "amqp_virtual_host")

    if config_file.has_option("rabbitmq", "amqp_exchange"):
        amqp_exchange = config_file.get("rabbitmq",
                                                "amqp_exchange")

    if config_file.has_option("rabbitmq", "amqp_exchange_type"):
        amqp_exchange_type = config_file.get("rabbitmq",
                                                "amqp_exchange_type")

    if config_file.has_option("webpy", "webpy_cache"):
        try:
            webpy_cache = config_file.getboolean("webpy",
                                             "webpy_cache")
        except ValueError:
            print "Configuration file problem: webpy_cache must be a " \
                  "boolean value."
            sys.exit(1)

    if config_file.has_option("logging", "log_file"):
        log_file = config_file.get("logging",
                                        "log_file")

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
