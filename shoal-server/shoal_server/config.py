from os.path import join, expanduser, exists, abspath
import sys
import ConfigParser
import logging

"""Setup shoal using config file.
   setup will look for a configuration file specified in the following order:
     directory of shoal-server
     /etc/shoal/shoal_server.conf
     ~/.shoal/shoal_server.conf
   The first one found will be used.
"""

SHOAL_DIR = '/var/shoal/'

# set default values dictionary,
# add new keys here, and they will automatically be populated
settings = {
    # Tornado Specific Section
    'tornado': {
        'shoal_dir':          { 'default_value': SHOAL_DIR,
                                'type': 'string' },
        'static_path':        { 'default_value': join(SHOAL_DIR, 'static'),
                                'type': 'string' },
        'template_path':     { 'default_value': join(SHOAL_DIR, 'templates'),
                                'type': 'string' },
        'port':               { 'default_value': 80,
                                'type': 'int' },
    },
    # General Section
    'general': {
        'geolitecity_path':   { 'default_value': join(SHOAL_DIR, 'bin'),
                                'type': 'string' },
        'geolitecity_url':    { 'default_value': 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
                                'type': 'string' },
        'geolitecity_update': { 'default_value':2592000,
                                'type': 'int' },
        'debug':              { 'default_value': False,
                                'type': 'bool' },
    },
    # Squid Section
    'squid': {
        'cleanse_interval': { 'default_value': 15,
                              'type': 'int' },
        'inactive_time':    { 'default_value': 180,
                              'type': 'int' },
    },
    # Redis Section
    'redis': {
        'port': { 'default_value': 6379,
                  'type': 'int' },
        'host': { 'default_value': 'localhost',
                  'type': 'string' },
        'db':   { 'default_value': 0,
                  'type': 'int' },
    },
    # RabbitMQ Section
    'rabbitmq': {
        'host':          { 'default_value': 'localhost',
                           'type': 'string' },
        'port':          { 'default_value': 5672,
                           'type': 'int' },
        'virtual_host':  { 'default_value': '/',
                           'type': 'string' },
        'exchange':      { 'default_value': 'shoal',
                           'type': 'string' },
        'exchange_type': { 'default_value': 'topic',
                           'type': 'string' },
        'use_ssl':       { 'default_value': False,
                           'type': 'bool' },
        'ca_cert':       { 'default_value': '',
                           'type': 'string' },
        'client_cert':   { 'default_value': '',
                           'type': 'string' },
        'client_key':    { 'default_value': '',
                           'type': 'string' },
        'reconnection_attempts': { 'default_value': 10,
                                   'type': 'int' },
    },
    # Logging Section
    'logging': {
        'log_file': { 'default_value': '/var/log/shoal_server.log',
                      'type': 'string' },
    'log_level': { 'default_value': logging.ERROR,
                        'type': 'string' },
    },
}

def setup():
    homedir = expanduser('~')

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

    # Get values set in config file and update settings dictionary
    for section in settings.keys():
        for key in settings[section]:
            try:
                if config_file.has_option(section, key):
                    if settings[section][key]['type'] == 'int':
                        try:
                            settings[section][key] = config_file.getint(section, key)
                        except ValueError:
                            print "Configuration file problem: %s must be an " \
                                    "int value." % key
                            exit(1)
                    elif settings[section][key]['type'] == 'bool':
                        try:
                            settings[section][key] = config_file.getboolean(section, key)
                        except ValueError:
                            print "Configuration file problem: %s must be an " \
                                    "boolean value." % key
                            exit(1)
                    else:
                        settings[section][key] = config_file.get(section, key)
                else:
                    settings[section][key] = settings[section][key]['default_value']
            except Exception as e:
                pass

def setup_ssl():
    try:
        settings['rabbitmq']['ca_cert'] = abspath(config_file.get("rabbitmq", "ca_cert"))
        settings['rabbitmq']['client_cert'] = abspath(config_file.get("rabbitmq", "client_cert"))
        settings['rabbitmq']['client_key']  = abspath(config_file.get("rabbitmq", "client_key"))
    except Exception as e:
        print "Configuration file problem: could not load SSL certs"
        print e
        sys.exit(1)

def setup_logging():
    if type(settings['logging']['log_level']) != int:
        try:
            settings['logging']['log_level'] = getattr(logging, settings['logging']['log_level'].upper())
        except Excetpion as e:
            print e

    # setup logging.
    log_format = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)s] - %(message)s'
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format=log_format,
                        datefmt='%m-%d %H:%M',
                        filename=settings['logging']['log_file'])
    # define a Handler which writes INFO messages or higher to the sys.stderr
    if settings['general']['debug']:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter(log_format)
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

setup()
setup_logging()
if settings['rabbitmq']['use_ssl']:
    setup_ssl()

