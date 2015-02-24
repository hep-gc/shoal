#Shoal Agent v0.8.X README

##Basic Commands
With the basic `shoal_agent` init script you can do the following:

```
service shoal-agent start
service shoal-agent stop
service shoal-agent reload 
service shoal-agent status
service shoal-agent force-restart
```

##Installation

The **best** way to install is with yum using our provided repositories. The impatient should skip to the Recommended Method section below.

If yum is used to install the Shoal RPM, then the Shoal Agent files will be placed in the standard system locations.
Otherwise, Shoal can be installed in your home directory or elsewhere, without needing root privileges.

In either case, the Shoal agent does not require root privilege to run. The init script uses the `nobody` user by default, although this is adjustable.

 _**Note**: Requires you have Python 2.6+, and the pika python module (available from EPEL)._

_**Note**: Shoal config files will be located either at `/etc/shoal/` or `~/.shoal/` depending on the installation method_

###Recommended Method: Use yum

First install [EPEL](http://fedoraproject.org/wiki/EPEL) (est. ~5 min)

    sudo yum install epel-release
    sudo yum update

Get the Shoal yum repository:

    sudo curl http://shoal.heprc.uvic.ca/repo/shoal.repo -o /etc/yum.repos.d/shoal.repo
   
Install the agent:

    sudo rpm --import http://hepnetcanada.ca/pubkeys/igable.asc
    sudo yum install shoal-agent

Configure the agent and start it:

    vim /etc/shoal/shoal_agent.conf
    service shoal-agent start

 _**Note**: Configuration of boolean variables
global_access: Set this to true if the squid is accessible globally and can be
served to whoever is close.

domain_access: Set this to true if the squid is globally available but you want
to confine access to clients from the same domain only.

Set both to false if the squid is behind a firewall or cannot be accessed from outside.

 _**Note**: A geoip domain database is requied to use these boolean features.


###Other Methods
1. [Install EPEL](http://fedoraproject.org/wiki/EPEL)
2. `yum install python-pika python-netifaces`
3. Use either Pip OR checkout from Github:
 - Using Pip: `pip install shoal-agent` 
 - Using Github: `svn co https://github.com/hep-gc/shoal/trunk/shoal-agent` and `python setup.py install`
4. Modify the settings in `shoal_agent.conf` as needed.
5. If the installation is not in a system location, the init script could be used if modified
6. Otherwise, use the init script and chkconfig to start Shoal. 

