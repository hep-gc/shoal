# Shoal v0.1 README
A squid cache publishing and advertising tool designed to work in fast changing environments.

## Overview

   * Each squid server will send an AMQP json encoded message to a centralized RabbitMQ server queue.
   * A webserver will retrieve the messages from the queue and maintain a list of active squids.
   * A newly booted virtual machine will query the webserver via a RESTful API to retrieve the IP of the nearest squid server.

### How to Install
    
More information coming soon...

### Basic configurations

More information coming soon...

### How to run

More information coming soon...

## LICENSE
This program is free software; you can redistribute it and/or modify it under the terms of either:

a) the GNU General Public License as published by the Free Software Foundation; either version 3, or (at your option) any later version, or

b) the Apache v2 License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See either the GNU General Public License or the Apache v2 License for more details.

You should have received a copy of the Apache v2 License with this software, in the file named "LICENSE".

You should also have received a copy of the GNU General Public License along with this program in the file named "COPYING". If not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA or visit their web page on the internet at http://www.gnu.org/copyleft/gpl.html.
