# Shoal Server README
# Version: v1.0.X
## Services
**Shoal Server** provides two services that can be utilized by clients.

### RESTful API
Clients can use the Shoal Server RESTful API to retrieve a list of nearest squids. Assuming Shoal Server is running on `localhost` the following commands can be used:

- To get a list of the default 5 nearest verified squids use:
  - `http:localhost/nearestverified`
- To retrieve a variable size of nearest verified squids you can use `http://localhost/nearestverified/<# of squids>`. For example to retrieve the closest 20 squid servers you can use:
  - `http://localhost/nearestverified/20`

- The extension 'nearest' returns the same as 'nearestverified', specifically `http://localhost/nearestverified/20` is the same as `http://localhost/nearest/20`.  Previously these did different things, but their functionality has now been merged. Both are kept to maintain compatibility with previous versions of Shoal Client.

- To get a list of all squids stored in shoal use:
  - `http://localhost/all`
 
### WPAD
Shoal Server has a basic implementation of the [WPAD](http://en.wikipedia.org/wiki/Web_Proxy_Autodiscovery_Protocol) standard.

- To retrieve a WPAD file containing the 5 closest squids you can visit:
  - `http://localhost/wpad.dat`

### Optional Features
The new release of shoal has several new optional features
- Verification
  - The new verification feature ids toggleable in the shoal_server configuration file
  - Shoal server will verify the squids advertised by shoal agents by checking their connectivity and attempting to download a common file from a repo on the proxy.
- Access Levels (requires GeoIP domain database**)
  - Shoal server will intelligently serve proxies to requesters based on Access Levels
  - Access Levels are configurable on the shoal-agents with 3 levels of access
    - Global: accessible from anywhere and will be served to any requester
    - Same Domain Only: accessible from anywhere but will only be served by requesters from the same domain (can still be verified)
    - No Outside Access: only accessible from inside the network due to firewall or other configuration, only served to requesters from same domain (cannot be verified)

- **GeoIP2 Domain database will have to be manually placed in the proper directory default:**
  - `/var/www/shoal/static/db/`

## Installation

 _**Note**: Requires you have a working RabbitMQ AMQP Server, and Python 3.6+_.
_Recommended to use a system wide install (sudo), but works in a virtualenv with tweaks_.


_**Note**: Shoal static files will be located either at `~/shoal_server/` or `/var/shoal/` if sudo was used_

_**Note**: Shoal config files will be located either at `~/.shoal/` or `/etc/shoal/` if sudo was used_

### Using Git (requires manual file placemet)

_**Note**: Some file permissions may need to be changed, check /var/log/shoal_server.log and /var/log/httpd/error_log for details._

_**Note**: Requires you have a working RabbitMQ AMQP Server, Python 3.6+, and apache with a working version of mod_wsgi_

_**Reference Reading**:_
  - [Install RabbitMQ Server on CentOS 7](https://www.howtoforge.com/tutorial/how-to-install-rabbitmq-server-on-centos-7/)

  - [Install mod_wsgi](https://www.ionos.com/community/hosting/python/use-mod-wsgi-to-run-python-as-a-web-application-on-centos-7/)


1. `git clone git://github.com/hep-gc/shoal.git`
1. `cd shoal/shoal-server/`
1. (optional) Make sure domain database is in /shoal-server/static/db/ prior to next step or it will not have the domain lookup functionality
1. `python setup.py install`
1. Move data and configuration files from `/usr/share/shoal-server/` to their proper locations:
	- `/usr/share/shoal-server/conf/shoal_server.conf` --> `/etc/shoal/shoal_server.conf`   (file)
	- `/usr/share/shoal-server/conf/shoal-server.logrotate` --> `/etc/logrotate.d/shoal-server` (file)
	- `/usr/share/shoal-server/scripts/` --> `/var/www/shoal/scripts/` (folder)
	- `/usr/share/shoal-server/static/`  --> `/var/www/shoal/static/` (folder)
	- `/usr/share/shoal-server/templates/` --> `/var/www/shoal/templates/` (folder)
	- `/usr/share/shoal-server/conf/shoal.conf`   --> `/etc/httpd/conf.d/` (file)
	
1. Check settings in `shoal_server.conf` update as needed. Make sure RabbitMQ server is running: `systemctl restart rabbitmq-server`
 
1. Update owner of /var/www directory to apache
	```
	$ sudo chown -R apache.apache /var/www
	```
1. If there is no file /var/log/shoal_server.log, create on and change the owner to apache
	```
	$ cd /var/log
	$ touch shoal_server.log
	$ chown -R apache.apache /var/log/shoal_server.log
	```
1. Might need to [disable the SELinux permanently](https://www.cyberciti.biz/faq/disable-selinux-on-centos-7-rhel-7-fedora-linux/), but make sure to double check
	```
	$ sestatus (check the status of selinux)
	$ sudo vi /etc/selinux/config (and then set SELINUX=disabled)
	(if disable it temporarily)
	$ sudo setenforce Permissive
	```
1. Restart the web server should see the page now says "List of Active Squids", and the list is empty
	```
	$ sudo service httpd restart
	```
 
1. Visit `http://localhost`
