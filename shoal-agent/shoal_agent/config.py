from __future__ import print_function

import requests
import re
import socket
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
use_credentials = False
amqp_username = ''
amqp_password = ''
use_ssl = False
amqp_ca_cert = ''
amqp_client_cert = ''
amqp_client_key = ''
external_ip = None
dnsname = None
interface = None
interval = 30
cloud = ''
cache_type = 'squid'
upstream = 'both'
cache_port = 3128
cache_auto_config = False
log_file = '/var/log/shoal_agent.log'
logging_level = logging.ERROR
#this value should be false unless you wish the shoal server to neglect verifying this cache
verified = False
#this is the speed of the network interface card in terms of KB/s
max_load = 122000
load_factor = 0.9

sender_email = 'root@localhost'
receiver_email = 'root@localhost'
email_subject = 'Shoal Agent Notification'
email_content = 'Hello, there is no cache servers running on the agent, please review the cache status. Trying to find a cache process automatically will be retried in 30 min. Thanks!'
last_sent_email = '/var/tmp/last_sent_email'

test_targeturl = "http://cvmfs-stratum-one.cern.ch/cvmfs/atlas.cern.ch/.cvmfswhitelist"

# auto config
# get cache port based on detected cache type
cache_process_name = 'squid'
cache_user = 'squid'
default_cache_port = 3128
hostname = socket.gethostname()

def detect_cache_type():
    try:
        check_output(['pidof', '-s', 'squid'])
        return 'squid', 'squid', 3128
    except:
        pass

    try:
        check_output(['pidof', '-s', 'varnishd'])
        return 'varnish', 'varnish', 6081
    except:
        pass

    return 'squid', 'squid', 3128  
    
def getString(content):
    try:
        formatted = bytes(content, 'utf-8')
    except:
        formatted = bytes(content) # for python 2
    return formatted
    
def detect_upstream(cache_type, hostname, port):
    if cache_type == 'varnish':
        targeturl = f"http://{hostname}:{port}/cvmfs/oasis.opensciencegrid.org/.cvmfspublished"
        repo = re.search("cvmfs\/(.+?)(\/|\.)|opt\/(.+?)(\/|\.)", targeturl).group(1)
        if repo is None:
            repo = re.search("cvmfs\/(.+?)(\/|\.)|opt\/(.+?)(\/|\.)", targeturl).group(3)
        file = requests.get(targeturl, timeout=2)
        f = file.content
        for line in f.splitlines():
            if line.startswith(getString('N')):
                if getString(repo) in line:
                    return 'cvmfs'
        return 'frontier'
    else:
        return 'both'

detected_type, detected_user, detected_port = detect_cache_type()
cache_type = detected_type
cache_process_name = detected_type if detected_type == 'squid' else 'varnishd'
cache_user = detected_user
default_cache_port = detected_port

try:
    cache_pid = int(check_output(['pidof', '-s', cache_process_name]))
    if cache_type == 'squid':
        cache_uid = getpwnam(cache_user)[2]
        def get_cache_port(filename):
            with open(filename) as f:
                for i, line in enumerate(f):
                    if i != 0:
                        lineList = line.strip().split()
                        if int(lineList[7]) == int(cache_uid):
                            if int(lineList[1].split(':')[0],16) == 0:
                                return int(lineList[1].split(':')[1],16)
                return None
        cache_port = get_cache_port('/proc/' + str(cache_pid) + '/net/tcp') or default_cache_port
        cache_port = get_cache_port('/proc/' + str(cache_pid) + '/net/tcp6') or cache_port
        cache_auto_config = True
    elif cache_type == 'varnish':
        cmdline = check_output(['ps', '-p', str(cache_pid), '-o', 'args', '--no-headers']).decode('utf-8')
        port_match = re.search(r'-a\s+(?:http=)?:(\d+)', cmdline)
        if port_match:
            cache_port = int(port_match.group(1))
            cache_auto_config = True
        else:
            cache_port = default_cache_port
except:
    cache_port = default_cache_port
    print("Couldn't auto config the cache port, use the default one ", cache_port)

upstream = detect_upstream(detected_type, hostname, cache_port)

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

if config_file.has_option("rabbitmq", "use_credentials") and config_file.getboolean("rabbitmq", "use_credentials"):
    use_credentials = True
    amqp_username = config_file.get("rabbitmq", "amqp_username")
    amqp_password = config_file.get("rabbitmq", "amqp_password")

if config_file.has_option("general", "interval"):
    try:
        interval = config_file.getint("general", "interval")
    except ValueError:
        print("Configuration file problem: interval must be an " \
              "integer value.")
        sys.exit(1)

if config_file.has_option("general", "cloud"):
    cloud = config_file.get("general", "cloud")

if config_file.has_option("general", "external_ip"):
    external_ip = config_file.get("general", "external_ip")

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


if config_file.has_option("general", "cache_port") and not cache_auto_config:
    cache_port = config_file.get("general", "cache_port")
    
if config_file.has_option("general", "max_load"):
    max_load = config_file.get("general", "max_load")

if config_file.has_option("general", "admin_email"):
    receiver_email = config_file.get("general", "admin_email")
