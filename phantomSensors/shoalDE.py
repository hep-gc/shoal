import os
import sys
import time
import json
import requests
import urllib
import ConfigParser
import subprocess

config = ConfigParser.ConfigParser()
config.read("./phantomDEParameters.config")

class shoalDecisionEngine(object):

    def __init__(self):
      
      self.api_url = "https://phantom.nimbusproject.org/api/dev"
       
      #Get an API Token
      #Construct username / password string
      userStr = "username=" + config.get("general", "USER") + "&"  \
              + "password=" + config.get("general", "password")
      #Get token from phantom using curl
      tokenAsJSONStr = subprocess.check_output(["curl", "-d", userStr, self.api_url +"/token"])
      #load returned JSON string as a dictionary
      tokenDict = json.loads(tokenAsJSONStr)

      if not tokenDict["success"]:
	sys.exit("Could not get phantom api token")

      self.user_id = tokenDict["user"]
      self.token   = tokenDict["token"]

      self.domain_name        = config.get("general", "DOMAIN")
      self.domainID           = 0 # set on creation of domain
      self.launch_config_name = config.get("general", "LAUNCH_CONFIG")
      self.launchConfigID     = 0 # set on creation of domain
      self.vm_image           = config.get("general", "VM_IMAGE")
      self.image_type         = config.get("general", "VM_IMAGE_TYPE")           
      self.key_name           = config.get("general", "KEY")
      self.clouds             = json.loads(config.get("general", "CLOUDS"))

      self.shoalURL = config.get("general", "SHOAL_SERVER")
      self.shoalLoad = 0
      self.shoalPrevLoad = 0	

      self.scaleDownThreshold = config.getint("general", "SCALE_DOWN_THRESH")
      self.scaleDownAmount    = config.getint("general", "SCALE_DOWN_AMOUNT")
      self.scaleUpThreshold   = config.getint("general", "SCALE_UP_THRESH")
      self.sacleUpAmount      = config.getint("general", "SCALE_UP_AMOUNT")
      self.minimumVMs         = config.getint("general", "MIN_VMS")
      self.maximumVMs         = config.getint("general", "MAX_VMS")
      self.updateInterval     = config.getint("general", "UPDATE_INTERVAL")

      self.createLaunchConfig()
      self.createDomain()
      self.run()
    
    def createLaunchConfig(self):
      # Get a list of existing launch configurations
      r = requests.get("%s/launchconfigurations" % self.api_url, auth=(self.user_id, self.token))
      existing_launch_configurations = r.json()
      existing_lc_names = [lc.get('name') for lc in existing_launch_configurations]

      # For now error if launch config already exsists
      if self.launch_config_name in existing_lc_names:
        sys.exit("Error launch config already exsists: %s" % self.launch_config_name)
      
      # Get ip of rabbitMQ server as user data for the launching squid
      # TODO might be PITA but could load this from shoal server config 
      # (if can assume this script runs on same machine as shoal server which, isn't necesary)
      rabbitMQIP = config.get("general", "RABBIT_MQ_IP")
      # If provided with localhost need to convert that to public ip
      if rabbitMQIP == "localhost":
        rabbitMQIP = subprocess.check_output("ifconfig eth0 |" + " grep 'inet addr:' |" \
                   + "cut -d: -f2 |" + " awk '{ print $1}'", shell=True)
        rabbitMQIP = rabbitMQIP.strip()	
      print "using rabbitMQ ip : %s" % rabbitMQIP

      print "Creating launch config '%s'" % self.launch_config_name
      new_lc = {
        'name': self.launch_config_name,
        'cloud_params': {},
	'contextualization_method': 'user_data'
      }

      rank = 0
      for cloud in self.clouds:
        rank = rank + 1
        cloud_param = {
                'image_id': self.vm_image,
                'instance_type': self.image_type,
                'max_vms': self.maximumVMs,
                'common': True,
                'rank': rank,
	        'user_data': rabbitMQIP
	        #TODO user data should probably use a JSON to make this more extendable
                #TODO doesn't work (user data probably needs to be more than just a string)
        }
        new_lc['cloud_params'][cloud] = cloud_param

      r = requests.post("%s/launchconfigurations" % self.api_url,
          data=json.dumps(new_lc), auth=(self.user_id, self.token))
      if r.status_code != 201:
        sys.exit("Error: %s" % r.text)

      r = requests.get("%s/launchconfigurations" % self.api_url, auth=(self.user_id, self.token))

      all_lcs = r.json()
      for lc in all_lcs:
        if lc.get('name') == self.launch_config_name:
          self.launchConfigID = lc.get('id')
          break

    def createDomain(self):
      # Check if domain already exist
      r = requests.get("%s/domains" % self.api_url, auth=(self.user_id, self.token))
      existingDomains = r.json()

      for domain in existingDomains:
      	if domain.get('name') == self.domain_name:
          sys.exit("Error: domain already exists")

      # Create our domain
      print "Creating domain %s" % self.domain_name
      new_domain = {
    	'name': self.domain_name,
	'de_name': 'multicloud',
        'lc_name': self.launch_config_name,
	'vm_count': 0
      }
      r = requests.post("%s/domains" % self.api_url,
                         data=json.dumps(new_domain), auth=(self.user_id, self.token))
      if r.status_code != 201:
        sys.exit("Error: %s" % r.text)
      
      r = requests.get("%s/domains" % self.api_url, auth=(self.user_id, self.token))
      allDomains = r.json()
      for domain in allDomains:
        if domain.get('name') == self.domain_name:
          self.domainID = domain.get('id')
          break

    def getTotalLoadOnShoalServer(self):
      loadSum = 0
      try:
        f = urllib.urlopen(self.shoalURL)
        nearestJson = f.read()
        jd = json.loads(nearestJson)
        loadSum = 0
        for i in jd.keys():
          loadSum = loadSum + jd[i]['load']
        self.shoalLoad = loadSum
      except:
        #unable to read json, just use the last value
        self.shoalLoad = self.shoalPrevLoad

      self.shoalPrevLoad = self.shoalLoad

    def run(self):
      r = requests.get("%s/domains" % self.api_url, auth=(self.user_id, self.token))
      existingDomains = r.json()
      domainData = None
      for domain in existingDomains:
        if domain.get('name') == self.domain_name:
          domainData = domain
          break
      else:
        sys.exit("Couldn't get domain %s" % self.domain_name)

      vmCount = self.minimumVMs
      print "Starting shoal test with %d VMs" % vmCount

      domainData['vm_count'] = vmCount
      r = requests.put("%s/domains/%s" % (self.api_url, domain.get('id')),
                       data=json.dumps(domainData), auth=(self.user_id, self.token))

      prevVMCount = vmCount
      while True:
        try:
          self.getTotalLoadOnShoalServer()
        
	  #scale up/down based on thresholds
	  if self.shoalLoad < self.scaleDownThreshold:
            print "Load less than scale down threshold"
            vmCount -= self.scaleDownAmount
          elif self.shoalLoad > self.scaleUpThreshold:
            print "Load greater than scale up threshold"
	    vmCount += self.sacleUpAmount
        
 	  #lock vm count in to specified range
 	  if vmCount < self.minimumVMs: vmCount = self.minimumVMs
          if vmCount > self.maximumVMs: vmCount = self.maximumVMs
	   
	  #if number of vms needs to change
	  if vmCount is not prevVMCount:
	    print "Scaling to %d VMs" % vmCount
            domainData['vm_count'] = vmCount
            r = requests.put("%s/domains/%s" % (self.api_url, domain.get('id')),
                             data=json.dumps(domainData), auth=(self.user_id, self.token))
	  
	  vmCount = prevVMCount
          time.sleep(self.updateInterval)

        except KeyboardInterrupt:
          print "\nExiting Cleaning up domain and launch config"
          r = requests.delete("%s/domains/%s" % (self.api_url, self.domainID),
                               auth=(self.user_id, self.token))
          r = requests.delete("%s/launchconfigurations/%s" % (self.api_url, self.launchConfigID),
                                auth=(self.user_id, self.token))
          sys.exit() 

shoalDecisionEngine()     
