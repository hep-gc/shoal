#Shoal Agent v0.6.X README

##Basic Commands
With the basic `shoal_agent` init script you can do the following:

```
service shoal_agent start
service shoal_agent stop
service shoal_agent reload 
service shoal_agent status
service shoal_agent force-restart
```

##Installation

The **best** way to install is with yum using our provided repositories. The imapatient should skip to the Recomeneded Method section below.

If yum is used to install the Shoal RPM, then the Shoal agent files will be placed in the standard system locations.
Otherwise, Shoal can be installed your home directory without needing root privileges (or anywhere else).

In either case, the Shoal agent does not require root privilege to run. The init script uses the `nobody` user by default, although this is adjustable.

 _**Note**: Requires you have Python 2.6+, and the pika python module (available from EPEL)._

_**Note**: Shoal config files will be located either at `/etc/shoal/` or `~/.shoal/` depending on the installation method_

###Recommended Method: Use yum

First install [EPEL](http://fedoraproject.org/wiki/EPEL)

    sudo yum install yum-conf-epel
    sudo yum update

Get the Shoal yum repository:

    sudo curl http://shoal.heprc.uvic.ca/repo/prod/shoal.repo -o /etc/yum.repos.d/shoal.repo
   
Install the agent:

    sudo yum install shoal-agent

Configure the agent and start it:

    vim /etc/shoal/shoal_agent.conf`
    touch /var/log/shoal_agent.log
    chown nobody:nobody /var/log/shoal_agent.log
    sudo service shoal_agent start
    sudo /sbin/chkconfig --add shoal_agent


###Other Methods
1. [Install EPEL](http://fedoraproject.org/wiki/EPEL)
2. `yum install python-pika python-netifaces`
3. Use either Pip OR checkout from Github:
 - Using Pip: `pip install shoal-agent` 
 - Using Github: `svn co https://github.com/hep-gc/shoal/trunk/shoal-agent` and `python setup.py install`
4. Modify the settings in `shoal_agent.conf` as needed.
5. If the installation is not in a system location, the init script could be used if modified
6. Otherwise, use the init script and chkconfig to start Shoal. 

