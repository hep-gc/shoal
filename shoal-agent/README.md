#Shoal Agent README
#Version: v0.9.X

## Basic Commands
With the basic `shoal_agent` init script you can do the following:

```
service shoal-agent start
service shoal-agent stop
service shoal-agent reload 
service shoal-agent status
service shoal-agent force-restart
```

## Installation

The **best** way to install is with yum using our provided repositories. The impatient should skip to the Recommended Method section below.

If yum is used to install the Shoal RPM, then the Shoal Agent files will be placed in the standard system locations.
Otherwise, Shoal can be installed in your home directory or elsewhere, without needing root privileges.

In either case, the Shoal agent does not require root privilege to run. The init script uses the `nobody` user by default, although this is adjustable.

 _**Note**: Requires you have Python 2.6+, and the pika python module (available from EPEL)._

_**Note**: Shoal config files will be located either at `/etc/shoal/` or `~/.shoal/` depending on the installation method_

### Recommended Method: Use yum (est. ~5 min)

First install [EPEL](http://fedoraproject.org/wiki/EPEL) 

    sudo yum install epel-release
    sudo yum update

Get the Shoal yum repository:

    For SL6:
    sudo curl http://shoal.heprc.uvic.ca/repo/shoal-sl6x.repo -o /etc/yum.repos.d/shoal.repo

    For SL7:
    sudo curl http://shoal.heprc.uvic.ca/repo/shoal-sl7x.repo -o /etc/yum.repos.d/shoal.repo
   
Install the agent:

    sudo rpm --import http://shoal.heprc.uvic.ca/repo/pubkeys/heprc.asc
    sudo yum install shoal-agent

Configure the agent and start it:

    vim /etc/shoal/shoal_agent.conf
    service shoal-agent start


 _**Note**: A geoip domain database is requied on the shoal-server to use these boolean features.


### Hint for the ATLAS Experiment Users:

A complete shoal_agent.conf file for ATLAS can be obtained by:

    sudo curl http://shoal.heprc.uvic.ca/repo/shoal_agent.conf -o /etc/shoal/shoal_agent.conf


### Other Methods
  1. [Install EPEL](http://fedoraproject.org/wiki/EPEL)
  2. `yum install python-pika python-netifaces`
  3. Use either Pip OR checkout from Github:
    * Using Pip: `pip install shoal-agent` 
    * Using Github: `git clone https://github.com/hep-gc/shoal/trunk/shoal-agent` and `python setup.py install`
  4. Move configuration files from `/usr/share/shoal-agent/` to their proper locations:   
    * `/usr/share/shoal-agent/conf/shoal_agent.conf` --> `/etc/shoal/shoal_agent.conf`   
    * `/usr/share/shoal-agent/conf/shoal-agent.init` --> `/etc/init.d/shoal-agent`   
    * `/usr/share/shoal-agent/conf/shoal-agent.logrotate` --> `/etc/logrotate.d/shoal-agent`    
    * `/usr/share/shoal-agent/conf/shoal-agent.sysconfig` --> `/etc/sysconfig/shoal/shoal-agent`   
    * `/usr/share/shoal-agent/conf/shoal-agent.service` --> `/usr/lib/systemd/system/shoal-agent.service` (if necessary)   
  5. Modify the settings in `shoal_agent.conf` as needed.
  6. Start shoal agent: `service shoal-agent start`
