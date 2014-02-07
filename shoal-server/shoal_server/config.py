from os.path import join, expanduser, exists, abspath
import sys
import ConfigParser

"""Setup shoal using config file.
   setup will look for a configuration file specified in the following order:
     directory of shoal-server
     /etc/shoal/shoal_server.conf
     ~/.shoal/shoal_server.conf
   The first one found will be used.
"""

# set default values dictionary,
# add new keys here, and they will automatically be populated
settings = {
    # General Section
    'general': {
        'shoal_dir':          { 'value': '/var/shoal/',
                                'type': 'int' },
        'static_path':        { 'value': '',
                                'type': 'string' },
        'templates_path':     { 'value': '',
                                'type': 'string' },
        'port':               { 'value': 80,
                                'type': 'int' },
        'geolitecity_path':   { 'value': '',
                                'type': 'string' },
        'geolitecity_url':    { 'value': 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
                                'type': 'string' },
        'geolitecity_update': { 'value':2592000,
                                'type': 'int' },
    },
    # Squid Section
    'squid': {
        'cleanse_interval': { 'value': 15,
                              'type': 'int' },
        'inactive_time':    { 'value': 180,
                              'type': 'int' },
    },
    # Redis Section
    'redis': {
        'port': { 'value': 6379,
                  'type': 'int' },
        'host': { 'value': 'localhost',
                  'type': 'string' },
        'db':   { 'value': 0,
                  'type': 'int' },
    },
    # RabbitMQ Section
    'rabbitmq': {
        'host':          { 'value': 'localhost',
                           'type': 'string' },
        'port':          { 'value': 5672,
                           'type': 'int' },
        'virtual_host':  { 'value': '/',
                           'type': 'string' },
        'exchange':      { 'value': 'shoal',
                           'type': 'string' },
        'exchange_type': { 'value': 'topic',
                           'type': 'string' },
        'use_ssl':       { 'value': False,
                           'type': 'bool' },
        'ca_cert':       { 'value': '',
                           'type': 'string' },
        'client_cert':   { 'value': '',
                           'type': 'string' },
        'client_key':    { 'value': '',
                                'type': 'string' },
    },
    # Logging Section
    'logging': {
        'log_file': { 'value': '/var/log/shoal_server.log',
                      'type': 'string' },
    },
    # Error Section
    'error': {
        'reconnect_time':     { 'value': 30,
                                'type': 'int' },
        'reconnect_attempts': { 'value': 10,
                                'type': 'int' },
    },
}

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
            if settings[section][key]['type'] == 'string':
                settings[section][key]['value'] = config_file.get(section, key)
            if settings[section][key]['type'] == 'int':
                try:
                    settings[section][key]['value'] = config_file.getint(section, key)
                except ValueError:
                    print "Configuration file problem: %s must be an " \
                            "boolean value." % key
                    exit(1)
            if settings[section][key]['type'] == 'bool':
                try:
                    settings[section][key]['value'] = config_file.getboolean(section, key)
                except ValueError:
                    print "Configuration file problem: %s must be an " \
                            "boolean value." % key
                    exit(1)
        except Exception as e:
            pass

if settings['rabbitmq']['use_ssl']['value']:
    try:
        settings['rabbitmq']['ca_cert']['value'] = abspath(config_file.get("rabbitmq", "ca_cert"))
        settings['rabbitmq']['client_cert']['value'] = abspath(config_file.get("rabbitmq", "client_cert"))
        settings['rabbitmq']['client_key']['value']  = abspath(config_file.get("rabbitmq", "client_key"))
    except Exception as e:
        print "Configuration file problem: could not load SSL certs"
        print e
        sys.exit(1)

if not settings['general']['static_path']['value']:
    settings['general']['static_path']['value'] = join(settings['general']['shoal_dir']['value'], 'static')
if not settings['general']['templates_path']['value']:
    settings['general']['templates_path']['value'] = join(settings['general']['shoal_dir']['value'], 'templates')
