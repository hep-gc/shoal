#!/usr/bin/python
import os
import sys
import json
import ConfigParser
import subprocess


def updateConfig(config, configFile, userDataJSON):
  try:
    config.read(configFile)  
    config.set('rabbitmq', "amqp_server_url", userDataJSON["rabbitMQServerIP"])
    config.set('rabbitmq', "amqp_port",       userDataJSON["rabbitMQServerPort"])
    with open(configFile, "w") as cf:
      config.write(cf)
  except:
    #this might not matter there are two config files
    pass

try:
  userDataServer  = subprocess.check_output(["cat", "/var/nimbus-metadata-server-url"])
  userDataJSONStr = subprocess.check_output(["curl", userDataServer + "/latest/user-data"])
  userDataJSON    = json.loads(userDataJSONStr)
except Exception as e:
  print e
  sys.exit("Could not read user data, exiting")

homedir = os.path.expanduser('~')
#config file can be in two places
configFile  = os.path.abspath(homedir + "/shoal/shoal-agent/shoal_agent.conf")
configFile2 = "/etc/shoal/shoal_agent.conf"
config = ConfigParser.ConfigParser()

updateConfig(config, configFile,  userDataJSON)
updateConfig(config, configFile2, userDataJSON)

#good to start shoal agen
