# Shoal v0.1 README
A squid cache publishing and advertising tool designed to work in fast changing environments.

## Overview

   * Each squid server will send an AMQP json encoded message to a centralized RabbitMQ server exchange.
   * A webserver will retrieve the messages from the exchange and maintain a list of active squids.
   * A newly booted virtual machine will query the webserver and retrieve a json encoded string that contains the IP of the nearest squid server.

##Installation
 
###Easy Way (NYI)
1. soon....

###Hard Way
1. Move shoal subfolder to any working directory.
2. Adjust configuration file included, and move it to `/etc/`.
3. Install any missing packages using pip or easy_install:

        pika 0.9.1+
        web.py 0.3+
        pygeoip 0.2.5+

4. `python shoal.py` to start the service.
5. Visit to `http://localhost:8080` to see the list of active squids.

*Note: Requires you have a working RabbitMQ AMQP Server, and python 2.6+*

## LICENSE
This program is free software; you can redistribute it and/or modify it under the terms of either:

a) the GNU General Public License as published by the Free Software Foundation; either version 3, or (at your option) any later version, or

b) the Apache v2 License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See either the GNU General Public License or the Apache v2 License for more details.

You should have received a copy of the Apache v2 License with this software, in the file named "LICENSE".

You should also have received a copy of the GNU General Public License along with this program in the file named "COPYING". If not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA or visit their web page on the internet at http://www.gnu.org/copyleft/gpl.html.
