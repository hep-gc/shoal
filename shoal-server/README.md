# Shoal-Server v0.1 README

##Installation
 
###Easy Way

_Recommended to use a system wide install (sudo), but works with virtualenv with tweaks_

1. Use `pip` or `easy_install`
  - `easy_install shoal-server`

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

