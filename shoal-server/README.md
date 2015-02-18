# Shoal Server v0.7.X README

##Services
**Shoal Server** provides two services that can be utilized by clients.

###RESTful API
Clients can use the Shoal Server RESTful API to retrieve a list of nearest squids. Assuming Shoal Server is running on `localhost` the following commands can be used:

- To get a list of the default 5 nearest verified squids use:
 - 'http:localhost/nearestverified'
- To retrieve a variable size of nearest verified squids you can use `http://localhost/nearestverified/<# of squids>`. For example to retrieve the closest 20 squid servers you can use:
 - `http://localhost/nearestverified/20`

- To get a list of the default 5 nearest squids use:
 - `http://localhost/nearest`
- To retrieve a variable size of nearest squids you can use `http://localhost/nearest/<# of squids>`. For example to retrieve the closest 20 squid servers you can use:
 - `http://localhost/nearest/20`
 
-To get a list of all squids stored in shoal use:
 'http://localhost/all'
 
###Optional Features
The new release of shoal has several new optional features
- Verification
 - The new verification feature is toggleable in the shoal_server configuration file
 - Shoal server will verify the squids advertised by shoal agents by checking their connectivity and attempting to download a common file from a repo on the proxy.
- Access Levels (requires GeoIP domain database**)
 - Shoal server will intelligently serve proxies to requesters based on Access Levels
 - Access Levels are configurable on the shoal-agents with 3 levels of access
  - Global: accessible from anywhere and will be served to any requester
  - Same Domain Only: accessible from anywhere but will only be served by requesters from the same domain (can still be verified)
  - No Outside Access: only accessible from inside the network due to firewall or other configuration, only served to requesters from same domain (cannot be verified)

**GeoIP2 Domain database will have to be manually placed in the proper directory default:
`/var/www/shoal/static/db/`

###WPAD
Shoal Server has a basic implementation of the [WPAD](http://en.wikipedia.org/wiki/Web_Proxy_Autodiscovery_Protocol) standard.

- To retrieve a WPAD file containing the 5 closest squids you can visit:
  - `http://localhost/wpad.dat`

##Installation
 _**Note**: Requires you have a working RabbitMQ AMQP Server, and Python 2.6+_
_Recommended to use a system wide install (sudo), but works in a virtualenv with tweaks_

_**Note**: Shoal static files will be located either at `~/shoal_server/` or `/var/shoal/` if sudo was used_

_**Note**: Shoal config files will be located either at `~/.shoal/` or `/etc/shoal/` if sudo was used_

###Recommended Method: Use yum (Apache)
The Yum rpm will Install all the dependencies including apache and configure them for shoal.
The Yum install does NOT [install the rabbitmq-server](https://www.rabbitmq.com/install-rpm.html) which will be required if one is not already running somewhere.

First install [EPEL](http://fedoraproject.org/wiki/EPEL)

    sudo yum install epel-release
    sudo yum update

Get the Shoal yum repository:

    sudo curl http://shoal.heprc.uvic.ca/repo/shoal.repo -o /etc/yum.repos.d/shoal.repo
   
Install the server:

    sudo rpm --import http://hepnetcanada.ca/pubkeys/igable.asc
    sudo yum install shoal-server
    
Configure the server and start it:

    vim /etc/shoal/shoal_server.conf
    If the server is to be externam facing be sure to open port 80 for apache
    apachectl start

###Using Pip

1. `pip install shoal-server`

2. Check settings in `shoal_server.conf` update as needed. Make sure RabbitMQ server is running.

4. Start `shoal-server`
  - _First run make take a few seconds to start as it needs to download the GeoLiteCity database (~12MB)._

5. Visit `http://localhost:8080`

###Using Git

1. `git clone git://github.com/hep-gc/shoal.git`
2. `cd shoal/shoal-server/`
2.5 (optional) Make sure domain database is in /shoal-server/static/db/ prior to next step or it will not have the domain lookup functionality
3. `python setup.py install`
4. Check settings in `shoal_server.conf` update as needed. Make sure RabbitMQ server is running.
5. Start `shoal-server`
 - _First run make take a few seconds to start as it needs to download the GeoLiteCity database (~12MB)._
 
6. Visit `http://localhost:8080`