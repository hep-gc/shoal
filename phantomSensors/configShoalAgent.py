#!/usr/local/bin/python
import os
import sys
import json
import ConfigParser
import subprocess

try:
  config = ConfigParser.ConfigParser()
  config.read(os.path.abspath("~/shoal/shoal-agent/shoal_agent.conf"))
  
  userDataServer  = subprocess.check_output(["cat", "/var/nimbus-metadata-server-url"])
  userDataJSONStr = subprocess.check_output(["curl", userDataServer + "/latest/user-data"])
  print userDataJSONStr
  userDataJSON    = json.loads(userDataJSONStr)
except Exception as e:
  print e
  sys.exit("Could not read config file or user data, exiting")

#debugging
print userDataJSON

config.set("rabbitMQ", "amqp_server_url", userDataJSON["rabbitMQServerIP"])
config.set("rabbitMQ", "amqp_port",       userDataJSON["rabbitMQServerPort"])

#good to start shoal agent
