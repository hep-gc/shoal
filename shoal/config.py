import os
import sys
import logging
import ConfigParser

# Shoal Options Module

# set default values
geolitecity_path = os.path.abspath('GeoLiteCity.dat')
geolitecity_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
geolitecity_update = 2592000
squid_cleanse_interval = 15
squid_inactive_time = 180
amqp_server_url = 'localhost'
amqp_server_port = 5672
amqp_server_queue = 'squiddata'
amqp_exchange = 'shoal'
amqp_exchange_type = 'topic'
webpy_cache = False
webpy_template_dir = 'templates/'
log_file = '/var/tmp/shoal.log'
log_format = '%(asctime)s %(levelname)s %(message)s'
log_level = logging.WARNING

def setup(path=None):
    """Setup shoal using config file.
       setup will look for a configuration file specified in /etc/shoal.conf
    """
    global geolitecity_path
    global geolitecity_url
    global geolitecity_update
    global squid_cleanse_interval
    global squid_inactive_time
    global amqp_server_url
    global amqp_server_port
    global amqp_server_queue
    global amqp_exchange
    global amqp_exchange_type
    global webpy_cache
    global webpy_template_dir
    global log_file
    global log_format
    global log_level

    # find config file
    if not path:
        if os.path.exists("/etc/shoal.conf"):
            path = "/etc/shoal.conf"
        else:
            print >> sys.stderr, "Configuration file problem: There doesn't " \
                  "seem to be a configuration file. " \
                  "You can specify one in /etc/shoal.conf"
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

    if config_file.has_option("rabbitmq", "amqp_server_port"):
        try:
            amqp_server_port = config_file.getint("rabbitmq", "amqp_server_port")
        except ValueError:
            print "Configuration file problem: amqp_port must be an " \
                  "integer value."
            sys.exit(1)

    if config_file.has_option("rabbitmq", "amqp_server_queue"):
        amqp_server_queue = config_file.get("rabbitmq",
                                                "amqp_server_queue")

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

    if config_file.has_option("webpy", "webpy_template_dir"):
        webpy_template_dir = config_file.get("webpy",
                                                "webpy_template_dir")

    if config_file.has_option("logging", "log_file"):
        log_file = config_file.get("logging",
                                        "log_file")

    if config_file.has_option("logging", "log_format"):
        log_format = config_file.get("logging",
                                        "log_format")

    if config_file.has_option("logging", "log_level"):
        try:
            log_level = config_file.getint("logging",
                                            "log_level")
        except ValueError:
            print "Configuration file problem: log_level must be a " \
                  "integer value."
            sys.exit(1)
