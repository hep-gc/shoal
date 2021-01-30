from __future__ import print_function

from os.path import exists, join, abspath
import sys
import logging
try:
    import configparser
except ImportError:  # python < 3
    import ConfigParser as configparser

# Shoal Options Module
from socket import gethostbyaddr
from subprocess import check_output
from pwd import getpwnam
import stun
import netifaces

"""
Setup shoal using config file.
setup will look for a configuration file specified in the following directory:
/etc/shoal/shoal_agent.conf
"""

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
dnsname = None
interface = None
interval = 30
cloud = ''
squid_port = 3128
squid_auto_config = False
log_file = '/var/log/shoal_agent.log'
logging_level = logging.ERROR
#this value should be false unless you wish the shoal server to neglect verifying this squid
verified = False
#this is the speed of the network interface card in terms of KB/s
max_load = 122000
load_factor = 0.9

sender_email = 'root@localhost'
receiver_email = 'root@localhost'
email_subject = 'Shoal Agent Notification'
email_content = 'Hello, there is no available squid running on the agent, please review the squid status. Trying to find a squid process automatically will be retried in 30 min. Thanks!'
last_sent_email = '/var/tmp/last_sent_email'

test_targeturl = "http://cvmfs-stratum-one.cern.ch/cvmfs/atlas.cern.ch/.cvmfswhitelist"

# auto config
# get squid_port
try:
    squid_uid = getpwnam('squid')[2]
    squid_pid = int(check_output(['pidof', '-s', 'squid']))
    def get_squid_port(filename):
        with open(filename) as f:
            for i, line in enumerate(f):
                if i != 0:
                    lineList = line.strip().split()
                    if int(lineList[7]) == int(squid_uid):
                        if int(lineList[1].split(':')[0],16) == 0:
                            return int(lineList[1].split(':')[1],16)
            return None
    squid_port = get_squid_port('/proc/' + str(squid_pid) + '/net/tcp') or squid_port
    squid_port = get_squid_port('/proc/' + str(squid_pid) + '/net/tcp6') or squid_port
    squid_auto_config = True
except:
    print("Couldn't auto config the squid port, use the default one ", squid_port)
# get external_ip
external_ip = stun.get_ip_info()[1]
# get dnsname
try:
    dnsname = gethostbyaddr(external_ip)[0]
    sender_email = 'root@' + dnsname
except:
    print("Couldn't auto config the domain name, use the default one ")
# get interface
for each_interface in netifaces.interfaces():
    try:
        for link in netifaces.ifaddresses(each_interface)[netifaces.AF_INET]:
            if link['addr'] == external_ip:
                interface = each_interface
                break
            elif not link['addr'].startswith('127.'):
                interface = each_interface
                break
    except Exception:
        continue
# get max_load
try:
    with open('/sys/class/net/' + interface + '/speed') as f:
        speed = int(f.readlines()[0])
        max_load = int(speed * 1000 * load_factor / 8)
except:
    print("Couldn't auto config the interface speed for max_load, use the default one")

# find config file by checking the directory of the calling script and sets path
if exists("/etc/shoal/shoal_agent.conf"):
    path = "/etc/shoal/shoal_agent.conf"
else:
    print( "Configuration file problem: There doesn't " \
              "seem to be a configuration file. " \
              "You can specify one in /etc/shoal/shoal_agent.conf",
           file=sys.stderr)
    sys.exit(1)

# Read config file from the given path above
config_file = configparser.ConfigParser()
try:
    config_file.read(path)
except IOError:
    print("Configuration file problem: There was a " \
          "problem reading %s. Check that it is readable," \
          "and that it exists. " % path,
          file=sys.stderr)
    raise
except configparser.ParsingError:
    print("Configuration file problem: Couldn't " \
          "parse your file. Check for spaces before or after variables.",
          file=sys.stderr)

    raise
except:
    print("Configuration file problem: There is something wrong with " \
          "your config file.")
    raise

# sets defaults to the options in the config file
if config_file.has_option("rabbitmq", "amqp_server_url"):
    amqp_server_url = config_file.get("rabbitmq", "amqp_server_url")

if config_file.has_option("rabbitmq", "amqp_port"):
    try:
        amqp_port = config_file.getint("rabbitmq", "amqp_port")
    except ValueError:
        print("Configuration file problem: amqp_port must be an " \
              "integer value.")
        sys.exit(1)

if config_file.has_option("rabbitmq", "use_ssl") and config_file.getboolean("rabbitmq", "use_ssl"):
    try:
        use_ssl = True
        amqp_ca_cert     = abspath(config_file.get("rabbitmq", "amqp_ca_cert"))
        amqp_client_cert = abspath(config_file.get("rabbitmq", "amqp_client_cert"))
        amqp_client_key  = abspath(config_file.get("rabbitmq", "amqp_client_key"))
    except Exception as e:
        print("Configuration file problem: could not load SSL certs")
        print(e)
        sys.exit(1)

if config_file.has_option("rabbitmq", "amqp_virtual_host"):
    amqp_virtual_host = config_file.get("rabbitmq", "amqp_virtual_host")

if config_file.has_option("rabbitmq", "amqp_exchange"):
    amqp_exchange = config_file.get("rabbitmq", "amqp_exchange")

if config_file.has_option("general", "interval"):
    try:
        interval = config_file.getint("general", "interval")
    except ValueError:
        print("Configuration file problem: interval must be an " \
              "integer value.")
        sys.exit(1)

if config_file.has_option("general", "cloud"):
    cloud = config_file.get("general", "cloud")

if config_file.has_option("logging", "log_file"):
    log_file = config_file.get("logging", "log_file")

if config_file.has_option("logging", "logging_level"):
    temp = config_file.get("logging", "logging_level")
    logLevels = {
                "DEBUG"    : logging.DEBUG,
                "INFO"     : logging.INFO,
                "WARNING"  : logging.WARNING,
                "ERROR"    : logging.ERROR,
                "CRITICAL" : logging.CRITICAL,
                }
    try:
        logging_level = logLevels[temp]
    except KeyError:
        print("Configuration file problem: Invalid logging level")
        sys.exit(1)

if config_file.has_option("general", "squid_port") and not squid_auto_config:
    squid_port = config_file.get("general", "squid_port")

if config_file.has_option("general", "max_load"):
    max_load = config_file.get("general", "max_load")

if config_file.has_option("general", "admin_email"):
    receiver_email = config_file.get("general", "admin_email")

