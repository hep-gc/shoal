from os.path import exists, expanduser, join
import sys
import ConfigParser

# Global settings
settings = {}

# set default values dictionary,
# add new keys here, and they will automatically be populated
default_settings = {
    # General Section
    'general': {
        'shoal_dir': '/var/shoal/',
        'static_path': '',
        'template_path': '',
        'port': 8080,
        'geolitecity_path': '',
        'geolitecity_url': 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
        'geolitecity_update': 2592000,
    },
    # Squid Section
    'squid': {
        'cleanse_interval': 15,
        'inactive_time': 180,
    },
    # Redis Section
    'redis': {
        'port': 6379,
        'host': 'localhost',
        'db': 0,
    },
    # RabbitMQ Section
    'rabbitmq': {
        'host': 'localhost',
        'port': 5672,
        'virtual_host': '/',
        'exchange': 'shoal',
        'exchange_type': 'topic',
        'use_ssl': False,
        'ca_cert': '',
        'client_cert': '',
        'client_key': '',
    },
    # Logging Section
    'logging': {
        'log_file': '/var/log/shoal_server.log',
    },
    # Error Section
    'error': {
        'reconnect_time': 30,
        'reconnect_attempts': 10
    },
}


def get_settings():
    temp_settings = dict(default_settings)
    path = "/etc/shoal/shoal_server.conf"
    if exists(path):
        parse_config(path, temp_settings)
    else:
        path = expanduser('~') + "/.shoal/shoal_server.conf"
        if exists(path):
            parse_config(path, temp_settings)
    return temp_settings


def parse_config(path, temp_settings):
    # Read config file from the given path above
    parser = ConfigParser.ConfigParser()
    try:
        parser.read(path)
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
    else:
        for sect in parser.sections():
            if sect not in temp_settings.keys():
                temp_settings[sect] = {}
            for option in parser.options(sect):
                temp_settings[sect][option] = parser.get(sect, option)


def update_settings():
    for i in settings.iteritems():
            print i
    if not settings['general']['static_path']:
        settings['general']['static_path'] = join(settings['general']['shoal_dir'], 'static')
    if not settings['general']['template_path']:
        settings['general']['template_path'] = join(settings['general']['shoal_dir'], 'templates')
    if not settings['general']['geolitecity_path']:
        settings['general']['geolitecity_path'] = join(settings['general']['shoal_dir'], 'bin')


# populate global settings dictionary
settings = get_settings()
# Update appropriate settings
update_settings()
