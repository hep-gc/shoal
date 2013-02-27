import os
import sys
import ConfigParser
import logging

# Shoal Options Module

# set default values
amqp_server_url = 'localhost'
amqp_server_port = 5672
amqp_exchange = 'shoal'
amqp_exchange_type = 'topic'
interval = 30
cloud = 'elephant'
log_file = '/var/tmp/shoal.log'
log_format = '%(asctime)s %(levelname)s %(message)s'
log_level = logging.WARNING


def setup(path=None):
    """Setup shoal using config file.
       setup will look for a configuration file specified in /etc/shoal_agent.conf
    """
    global amqp_server_url
    global amqp_server_port
    global amqp_exchange
    global amqp_exchange_type
    global interval
    global cloud
    global log_file
    global log_format
    global log_level

    # find config file
    if not path:
        if os.path.exists("/etc/shoal_agent.conf"):
            path = "/etc/shoal_agent.conf"
        else:
            print >> sys.stderr, "Configuration file problem: There doesn't " \
                  "seem to be a configuration file. " \
                  "You can specify one in /etc/shoal_agent.conf"
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

    if config_file.has_option("rabbitmq", "amqp_exchange"):
        amqp_exchange = config_file.get("rabbitmq",
                                                "amqp_exchange")

    if config_file.has_option("rabbitmq", "amqp_exchange_type"):
        amqp_exchange_type = config_file.get("rabbitmq",
                                                "amqp_exchange_type")

    if config_file.has_option("general", "interval"):
        try:
            interval = config_file.getint("general", "interval")
        except ValueError:
            print "Configuration file problem: amqp_port must be an " \
                  "integer value."
            sys.exit(1)

    if config_file.has_option("general", "cloud"):
        cloud = config_file.get("general",
                                   "cloud")

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
