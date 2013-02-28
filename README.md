# Shoal v0.1 README
A squid cache publishing and advertising tool designed to work in fast changing environments.

## Overview

   * Each squid server will send an AMQP json encoded message to a centralized RabbitMQ server exchange.
   * A webserver will retrieve the messages from the exchange and maintain a list of active squids.
   * A newly booted virtual machine will query the webserver via a RESTful API to retrieve the IP of the nearest squid server.

### How to Install
    
More information coming soon...

##Basic configurations
Change the shoal.conf file with your own settings in `/etc/shoal.conf`
###General
- Path to the GeoLiteCity database if not in root directory of shoal.
 - `geolitecity_path = '/usr/local/shoal/GeoLiteCity.dat`
- URL to download GeoLiteCity database. nIncase url ever changes).
 - `geolitecity_url = http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz`
- If GeoLiteCity database is older than this number (in seconds) it will update.
 - `geolitecity_update_time = 2592000`

###Squid
- Interval that ShoalUpdate will run to cleanse any inactive squids. This should be set to a reasonable number to keep the shoal up to date.
 - `squid_cleanse_interval = 15`
- Squids will be cleansed from the shoal if we have not received an amqp message from it within this time.
 - `squid_inactive_time = 180`

###RabbitMQ
*Note: see [RabbitMQ](http://www.rabbitmq.com) documentation for more info on these settings*

- The url of the RabbitMQ server.
 - `amqp_server_url = localhost`
- Queue to receive messages from.
 - `amqp_server_queue = squiddata`
- Port RabbitMQ server is running on. 
 - `amqp_server_port = 5672`
- Exchange used to send amqp messages.
 - `amqp_exchange = shoal`
- Type of exchange. 
 - `amqp_exchange_type = topic`

###Webpy
- Whether webpy should use its cache.
 - `webpy_cache = False`
- Where templates can be found (relative to shoal.py)
 - `webpy_template_dir = templates/`

### How to run

More information coming soon...

## LICENSE
This program is free software; you can redistribute it and/or modify it under the terms of either:

a) the GNU General Public License as published by the Free Software Foundation; either version 3, or (at your option) any later version, or

b) the Apache v2 License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See either the GNU General Public License or the Apache v2 License for more details.

You should have received a copy of the Apache v2 License with this software, in the file named "LICENSE".

You should also have received a copy of the GNU General Public License along with this program in the file named "COPYING". If not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA or visit their web page on the internet at http://www.gnu.org/copyleft/gpl.html.

