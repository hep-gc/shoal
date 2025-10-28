#!/usr/bin/env python

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
        """
            Constructor for shoalDecision Engine
            loads api token and gets default values from phantom config file
        """
        self.api_url = "https://phantom.nimbusproject.org/api/dev"
        self.loadApiToken()

        self.domain_name = config.get("general", "DOMAIN")
        self.domainID = 0 # set on creation of domain
        self.launch_config_name = config.get("general", "LAUNCH_CONFIG")
        self.launchConfigID = 0 # set on creation of domain
        self.vm_image = config.get("general", "VM_IMAGE")
        self.image_type = config.get("general", "VM_IMAGE_TYPE")
        self.key_name = config.get("general", "KEY")
        self.clouds = json.loads(config.get("general", "CLOUDS"))

        # shoalURL for heprc is http://shoal.heprc.uvic.ca/nearest
        self.shoalURL = config.get("general", "SHOAL_SERVER")
        self.shoalLoad = 0
        self.shoalPrevLoad = 0

        self.scaleDownThreshold = config.getint("general", "SCALE_DOWN_THRESH")
        self.scaleDownAmount = config.getint("general", "SCALE_DOWN_AMOUNT")
        self.scaleUpThreshold = config.getint("general", "SCALE_UP_THRESH")
        self.sacleUpAmount = config.getint("general", "SCALE_UP_AMOUNT")
        self.minimumVMs = config.getint("general", "MIN_VMS")
        self.maximumVMs = config.getint("general", "MAX_VMS")
        self.updateInterval = config.getint("general", "UPDATE_INTERVAL")

    def loadApiToken(self):
        """
            attempts to load a saved api token if it still works from the api_url launch configuration
            if it doesn't then it will get a new api token
        """
        tokenAsJSONStr =''
        tokenJSON = {}
        # attempt to load a saved token
        try:
            with open("savedToken", "r") as st:
                tokenAsJSONStr = st.read()
            tokenDict = json.loads(tokenAsJSONStr)
            # test it to see if it works/is still valid
            r = requests.get("%s/launchconfigurations" % self.api_url,
                              auth=(tokenDict["user"], tokenDict["token"]))
            # no good need a new one
            if r.status_code != 200:
                tokenDict = self.getNewApiToken()
        except:
            tokenDict = self.getNewApiToken()
        # set the token
        self.user_id = tokenDict["user"]
        self.token = tokenDict["token"]
     
    def getNewApiToken(self):
        """
            gets a new api token using the config file from the api_url
            writes it into savedToken and saves it in tokenDict as a JSON str
        """
        # Construct username / password string
        userStr = "username=" + config.get("general", "USER") + "&" \
                  + "password=" + config.get("general", "password")
        # Get token from phantom using curl
        tokenAsJSONStr = subprocess.check_output(["curl", "-s", "-d",
                                                userStr, self.api_url +"/token"])
        # save the token
        with open("savedToken", "w") as st:
            st.write(tokenAsJSONStr)
        # load returned JSON string as a dictionary
        tokenDict = json.loads(tokenAsJSONStr)
        # this script can't do anything without a token
        if not tokenDict["success"]:
            sys.exit("Could not get phantom api token")
        return tokenDict

    def createLaunchConfig(self):
        """
            if there are existing launch configurations, use those
            if not then it will create new lc from the rabbitMQ server ip and port
            initializes clouds for the lc and posts it back to lc api_url
        """
        # Get a list of existing launch configurations
        r = requests.get("%s/launchconfigurations" % self.api_url, auth=(self.user_id, self.token))
        existing_launch_configurations = r.json()
        existing_lc_names = [lc.get('name') for lc in existing_launch_configurations]

        # create new launch configurations
        if self.launch_config_name not in existing_lc_names:

            # Get ip of rabbitMQ server as user data for the launching cache proxy
            rabbitMQIP = config.get("general", "RABBIT_MQ_IP")
            # If provided with localhost need to convert that to public ip
            if rabbitMQIP == "localhost":
                rabbitMQIP = subprocess.check_output("ifconfig eth0 |" + " grep 'inet addr:' |" \
                                                   + "cut -d: -f2 |" + " awk '{ print $1}'", shell=True)
                rabbitMQIP = rabbitMQIP.strip()
            rabbitMQPort = config.get("general", "RABBIT_MQ_PORT")

            userDataDict = {}
            userDataDict["rabbitMQServerIP"] = rabbitMQIP
            userDataDict["rabbitMQServerPort"] = rabbitMQPort

            # initializes for new lc
            new_lc = {
                'name': self.launch_config_name,
                'cloud_params': {},
                'contextualization_method': 'user_data',
                'user_data': json.dumps(userDataDict)
            }

            # intializes clouds into lc
            rank = 0
            for cloud in self.clouds:
                rank = rank + 1
                cloud_param = {
                    'image_id': self.vm_image,
                    'instance_type': self.image_type,
                    'max_vms': self.maximumVMs,
                    'common': True,
                    'rank': rank
                }
                new_lc['cloud_params'][cloud] = cloud_param

            r = requests.post("%s/launchconfigurations" % self.api_url,
                data=json.dumps(new_lc), auth=(self.user_id, self.token))
            if r.status_code != 201:
                sys.exit("Error: %s" % r.text)

        else:
            print "Launch config already exists: %s" % (self.launch_config_name)

        # set launch configuration id
        r = requests.get("%s/launchconfigurations" % self.api_url, auth=(self.user_id, self.token))
        all_lcs = r.json()
        for lc in all_lcs:
            if lc.get('name') == self.launch_config_name:
                self.launchConfigID = lc.get('id')
                break

    def createDomain(self):
        """
            creates domain if it doesn't already exist
            uses standard multicloud DE and the launch configurations set up earlier with 0 VM's to start
            starts domain with our parameters
        """
        # Check if domain already exist
        r = requests.get("%s/domains" % self.api_url, auth=(self.user_id, self.token))
        existing_domains = r.json()

        domain_exists = False
        domain_id = None
        for domain in existing_domains:
            if domain.get('name') == self.domain_name:
                domain_exists = True
                domain_id = domain.get('id')
                break

        # Create our domain
        print "Creating domain: %s" % self.domain_name
        new_domain = {
            'name': self.domain_name,
            'de_name': 'multicloud',
            'lc_name': self.launch_config_name,
            'vm_count': 0
        }

        if not domain_exists:
            r = requests.post("%s/domains" % self.api_url,
                               data=json.dumps(new_domain), auth=(self.user_id, self.token))
            if r.status_code != 201:
                sys.exit("Error: %s" % r.text)
        else:
            r = requests.put("%s/domains/%s" % (self.api_url, domain_id),
                data=json.dumps(new_domain), auth=(self.user_id, self.token))

        # sets domain id
        r = requests.get("%s/domains" % self.api_url, auth=(self.user_id, self.token))
        all_domains = r.json()
        for domain in all_domains:
            if domain.get('name') == self.domain_name:
                self.domainID = domain.get('id')
                break

    def getTotalLoadOnShoalServer(self):
        """
            opens the url to shoal and gets the total load on the shoal server
        """
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
            # unable to read json, just use the last value
            self.shoalLoad = self.shoalPrevLoad

        self.shoalPrevLoad = self.shoalLoad

    def run(self):
        """
            First acquires the domain from api_url. It then scales amount of VM's 
            based on the current load compared to the threshold, but always stays
            within the min and max number of VM's given and then finally changes the domain data.
        """
        r = requests.get("%s/domains" % self.api_url, auth=(self.user_id, self.token))
        existing_domains = r.json()
        domain_data = None
        for domain in existing_domains:
            if domain.get('name') == self.domain_name:
                domain_data = domain
                break
        else:
            sys.exit("Couldn't get domain in run: %s" % self.domain_name)

        vmCount = self.minimumVMs
        print "Starting shoal test with %d VMs" % vmCount

        domain_data['vm_count'] = vmCount
        r = requests.put("%s/domains/%s" % (self.api_url, domain.get('id')),
                          data=json.dumps(domain_data), auth=(self.user_id, self.token))

        prevVMCount = vmCount
        while True:
            try:
                self.getTotalLoadOnShoalServer()
                print "Current shoal load: ", self.shoalLoad
                # scale up/down based on thresholds
                if self.shoalLoad < self.scaleDownThreshold:
                    print "Load less than scale down threshold %s" % (self.scaleDownThreshold)
                    vmCount -= self.scaleDownAmount
                elif self.shoalLoad > self.scaleUpThreshold:
                    print "Load greater than scale up threshold %s" % (self.scaleUpThreshold)
                    vmCount += self.sacleUpAmount

                # lock vm count in to specified range
                if vmCount < self.minimumVMs:
                    print "VM count reached minimum, bounded at %s VM's" % (self.minimumVMs)
                    vmCount = self.minimumVMs
                if vmCount > self.maximumVMs:
                    print "VM count reached maximum, bounded at %s VM's" % (self.maximumVMs)
                    vmCount = self.maximumVMs

                # if number of vms needs to change
                if vmCount is not prevVMCount:
                    print "Scaling to %d VMs" % vmCount
                    domain_data['vm_count'] = vmCount
                    r = requests.put("%s/domains/%s" % (self.api_url, domain.get('id')),
                                     data=json.dumps(domain_data), auth=(self.user_id, self.token))

                prevVMCount = vmCount
                time.sleep(self.updateInterval)

            except KeyboardInterrupt:
                print "\nExiting Cleaning up domain and launch config"
                r = requests.delete("%s/domains/%s" % (self.api_url, self.domainID),
                                     auth=(self.user_id, self.token))
                r = requests.delete("%s/launchconfigurations/%s" % (self.api_url, self.launchConfigID),
                                     auth=(self.user_id, self.token))
                sys.exit()

shoalDE = shoalDecisionEngine()
shoalDE.createLaunchConfig()
shoalDE.createDomain()
shoalDE.run()
