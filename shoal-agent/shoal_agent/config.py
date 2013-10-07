from os.path import exists, join, expanduser, abspath
import sys
import ConfigParser

# Shoal Options Module

# set default values
amqp_server_url = 'localhost'
amqp_port = 5672
amqp_virtual_host = '/'
amqp_exchange = 'shoal'
use_ssl = False
amqp_ca_cert = ''
amqp_client_cert = ''
amqp_client_key = ''
external_ip = None
interface = None
interval = 30
cloud = ''
squid_port = 3128
log_file = '/var/log/shoal_agent.log'


def setup(path=None):
    """Setup shoal using config file.
       setup will look for a configuration file specified in /etc/shoal/shoal_agent.conf
       or ~/.shoal/shoal_agent.conf
    """
    global amqp_server_url
    global amqp_virtual_host
    global amqp_exchange
    global external_ip
    global interface
    global interval
    global cloud
    global squid_port
    global log_file

    homedir = expanduser('~')

    # find config file
    if not path:
        if exists("/etc/shoal/shoal_agent.conf"):
            path = "/etc/shoal/shoal_agent.conf"
        elif exists(abspath(homedir + "/shoal/shoal-server/shoal_server.conf")):
            path = abspath(homedir + "/shoal/shoal-server/shoal_server.conf")
        else:
            print >> sys.stderr, "Configuration file problem: There doesn't " \
                  "seem to be a configuration file. " \
                  "You can specify one in /etc/shoal/shoal_agent.conf or ~/.shoal/shoal_agent.conf"
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

    if config_file.has_option("rabbitmq", "amqp_port"):
        amqp_port = config_file.get("rabbitmq", "amqp_port")

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

    if config_file.has_option("rabbitmq", "amqp_virtual_host"):
        amqp_virtual_host = config_file.get("rabbitmq",
                                                "amqp_virtual_host")

    if config_file.has_option("rabbitmq", "amqp_exchange"):
        amqp_exchange = config_file.get("rabbitmq",
                                                "amqp_exchange")

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

    if config_file.has_option("general", "squid_port"):
        try:
            squid_port = config_file.getint("general", "squid_port")
        except ValueError:
            print "Configuration file problem: amqp_port must be an " \
                  "integer value."
            sys.exit(1)

    if config_file.has_option("general", "external_ip"):
        external_ip = config_file.get("general",
                                                "external_ip")

    if config_file.has_option("general", "interface"):
        interface = config_file.get("general",
                                                "interface")
