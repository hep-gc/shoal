# Shoal-Server v0.3 README

##Services
**shoal-server** provides two services that can be utilized by clients.

###RESTful API
Clients can use the **shoal-server** REST API to retrieve a list of nearest squids. Assuming **shoal-server** is running at `localhost:8080` the following commands can be used:

- To get a list of the default 5 nearest squids use:
 - `http://localhost:8080/nearest`
- To retrieve a variable size of nearest squids you can use `http://localhost:8080/nearest/<# of squids>`. For example to retrieve the closest 20 squid servers you can use:
 - `http://localhost:8080/nearest/20`

###WPAD
**shoal-server** has a basic implementation of the [WPAD](http://en.wikipedia.org/wiki/Web_Proxy_Autodiscovery_Protocol) standard.

- To retrieve a WPAD file containing the 5 closest squids you can visit:
  - `http://localhost:8080/wpad.dat`

##Installation
 
###Easy Way

_Recommended to use a system wide install (sudo), but works with virtualenv with tweaks_

1. Use `pip`
  - `pip install shoal-server`

2. Location of files depending if **sudo** was used or not 
  - **Configuration Files:** `/etc/shoal/`
  - **Static Files:** `/var/shoal/`
  - Configuration Files: `~/.shoal/`
  - Static Files: `~/shoal_server/`

3. Make sure RabbitMQ server is running.

4. Start shoal server `service shoal_server start` or `shoal-server`
5. Visit `http://localhost:8080`

**NOTE:** _May need to tweak init.d script (`/etc/init.d/shoal_server`), or make sure executable `shoal-server` is in your PATH._


###Hard Way
1. Download Shoal-Server from [Shoal Project](http://github.com/hep-gc/shoal)
2. Move shoal-server subfolder to any working directory
3. Adjust configuration file included, and move it to `/etc/` or `~/.shoal/`
4. Install missing packages:
  - pika 0.9.1+
  - web.py 0.3+
  - pygeoip 0.2.5+

4. `python shoal_server.py` to start the server
5. Visit to `http://localhost:8080`

*Note: Requires you have a working RabbitMQ AMQP Server, and python 2.6+*

