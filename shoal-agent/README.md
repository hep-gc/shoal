# Shoal Agent README
# Version: v1.0.1


## Important to know about the configuration
The configuration has been simplified compared to previous versions and most settings are automatically configured at runtime.
There is also a setup script which should be run right after the pip install which will help to set the right options for the shoal-agent.
The config file is placed in /etc/shoal/shoal_agent.conf by the setup script and can be edited manually later on too.
The new shoal-agent is compatible with python3 as well as python2. It is recommended to use the python3 version.

## Included in frontier-squid, used by WLCG
The [frontier-squid](https://twiki.cern.ch/twiki/bin/view/Frontier/InstallSquid)
rpm distribution of squid (provided by the Worldwide LHC Computing Grid,
WLCG) includes shoal-agent which can be enabled in its
[configuration](https://twiki.cern.ch/twiki/bin/view/Frontier/InstallSquid#Enabling_discovery_through_WLCG).  It uses the same default shoal server. 
The WLCG also includes shoal-tracked squids in its Web Proxy Auto
Discovery service (see above configuration link).

## Basic Commands
With the basic `shoal_agent` init script you can do the following:

```
service shoal-agent start
service shoal-agent stop
service shoal-agent restart
```

## Installation

The **recommended** way to install is with pip.
Although, the Shoal agent does not require root privilege to run; by default the `shoal` user and group is used; it should be installed as root.
If the shoal user and group do not exist then the install script will create the entries in the system.

 _**Note**: Requires you have Python 2.6+, and the pika, netifaces python module (available from EPEL)._

### Recommended Method: Use pip (est. ~5 min)
  1. Login as root or become root via `sudo su -`
  2. Install shoal-agent using pip/pip3, e.g. `pip3 install shoal-agent`
  3. Run the installation script, `shoal-agent-installation.sh`, to setup your configuration
  
  

