#!/usr/local/bin/python
import os
import sys
import json
import ConfigParser
import subprocess

try:
  homedir = os.path.expanduser('~')
  configFile = os.path.abspath(homedir + "/shoal/shoal-agent/shoal_agent.conf")
  config = ConfigParser.ConfigParser()
  config.read(configFile)
  
  userDataServer  = subprocess.check_output(["cat", "/var/nimbus-metadata-server-url"])
  userDataJSONStr = subprocess.check_output(["curl", userDataServer + "/latest/user-data"])
  userDataJSON    = json.loads(userDataJSONStr)
except Exception as e:
  print e
  sys.exit("Could not read config file or user data, exiting")

config.set('rabbitmq', "amqp_server_url", userDataJSON["rabbitMQServerIP"])
config.set('rabbitmq', "amqp_port",       userDataJSON["rabbitMQServerPort"])

with open(configFile, "w") as cf:
  config.write(cf)

#good to start shoal agent
