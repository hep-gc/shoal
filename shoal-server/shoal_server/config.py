from os.path import exists, expanduser
import sys
import ConfigParser

# set default values dictionary,
# add new keys here, and they will automatically be populated
default_settings = {
    # General Section
    'general': {
        'shoal_dir': {'default_value': '/var/shoal/',
                      'type': 'int'},
        'static_path': {'default_value': '',
                        'type': 'string'},
        'template_path': {'default_value': '',
                          'type': 'string'},
        'port': {'default_value': 80,
                 'type': 'int'},
        'geolitecity_path': {'default_value': '',
                             'type': 'string'},
        'geolitecity_url': {'default_value': 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
                            'type': 'string'},
        'geolitecity_update': {'default_value': 2592000,
                               'type': 'int'},
    },
    # Squid Section
    'squid': {
        'cleanse_interval': {'default_value': 15,
                             'type': 'int'},
        'inactive_time': {'default_value': 180,
                          'type': 'int'},
    },
    # Redis Section
    'redis': {
        'port': {'default_value': 6379,
                 'type': 'int'},
        'host': {'default_value': 'localhost',
                 'type': 'string'},
        'db': {'default_value': 0,
               'type': 'int'},
    },
    # RabbitMQ Section
    'rabbitmq': {
        'host': {'default_value': 'localhost',
                 'type': 'string'},
        'port': {'default_value': 5672,
                 'type': 'int'},
        'virtual_host': {'default_value': '/',
                         'type': 'string'},
        'exchange': {'default_value': 'shoal',
                     'type': 'string'},
        'exchange_type': {'default_value': 'topic',
                          'type': 'string'},
        'use_ssl': {'default_value': False,
                    'type': 'bool'},
        'ca_cert': {'default_value': '',
                    'type': 'string'},
        'client_cert': {'default_value': '',
                        'type': 'string'},
        'client_key': {'default_value': '',
                       'type': 'string'},
    },
    # Logging Section
    'logging': {
        'log_file': {'default_value': '/var/log/shoal_server.log',
                     'type': 'string'},
    },
    # Error Section
    'error': {
        'reconnect_time': {'default_value': 30,
                           'type': 'int'},
        'reconnect_attempts': {'default_value': 10,
                               'type': 'int'},
    },
}


def parse_config():
    settings = {}
    path = "/etc/shoal/shoal_server.conf"
    if not exists(path):
        path = expanduser('~') + "/.shoal/shoal_server.conf"
        if not exists(path):
            settings = default_settings
    else:
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
                settings[sect] = {}
                for option in parser.options(sect):
                    settings[sect][option] = parser.get(sect, option)

    return settings
