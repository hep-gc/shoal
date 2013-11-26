#Shoal Agent v0.6.X README

##Basic Commands
With the basic `shoal_agent` init script you can do the following:
- Start Shoal Agent
 - `service shoal_agent start`
- Stop Shoal Agent
 - `service shoal_agent stop` 
- Restart Shoal Agent
 - `service shoal_agent reload` 
- Status of Shoal Agent
 - `service shoal_agent status` 
- Force restart Shoal Agent
 - `service shoal_agent force-restart`

##Installation

 _**Note**: Requires you have Python 2.6+, and the pika python module (available from EPEL)._

_**Note**: Shoal config files will be located either at `/etc/shoal/` or `~/.shoal/` depending on the installation method_

If YUM is used to install the Shoal RPM, then the Shoal agent files will be placed in the standard system locations.
Otherwise, Shoal can be installed in e.g. your home directory without needing root privileges.

In either case, the Shoal agent does not require root privilege to run. The init script uses the `nobody` user by default, although this is adjustable.

###Recommended Method: Use YUM
1. [Install EPEL](http://fedoraproject.org/wiki/EPEL)
2. `wget http://shoal.heprc.uvic.ca/repo/shoal.repo`
3. `sudo mv shoal.repo /etc/yum.repos.d/`
4. `sudo yum install shoal-agent`
5. Configure `/etc/shoal/shoal_agent.conf` as needed
6. Create `/var/log/shoal_agent.log` and chown it to the appropriate user
7. `sudo service shoal_agent start`
8. `sudo /sbin/chkconfig --add shoal_agent`

###Other Methods
1. [Install EPEL](http://fedoraproject.org/wiki/EPEL)
2. `yum install python-pika python-netifaces`
3. Use either Pip OR checkout from Github:
 - Using Pip: `pip install shoal-agent` 
 - Using Github: `svn co https://github.com/hep-gc/shoal/trunk/shoal-agent` and `python setup.py install`
4. Modify the settings in `shoal_agent.conf` as needed.
5. If the installation is not in a system location, the init script could be used if modified
6. Otherwise, use the init script and chkconfig to start Shoal. 

