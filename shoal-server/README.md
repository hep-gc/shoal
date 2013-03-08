# Shoal-Server v0.1 README

##Installation
 
###Easy Way (NYI)
1. soon....

###Hard Way
1. Move shoal-server subfolder to any working directory.
2. Adjust configuration file included, and move it to `/etc/`.
3. Install any missing packages using `pip` or `easy_install`:

        pika 0.9.1+
        web.py 0.3+
        pygeoip 0.2.5+

4. `python shoal_server.py` to start the service.
5. Visit to `http://localhost:8080` to see the list of active squids.

*Note: Requires you have a working RabbitMQ AMQP Server, and python 2.6+*
