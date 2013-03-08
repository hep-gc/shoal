# Shoal v0.1 README
A squid cache publishing and advertising tool designed to work in fast changing environments.

## Overview

   * Each squid server will send an AMQP json encoded message to a centralized RabbitMQ server exchange.
   * A webserver will retrieve the messages from the exchange and maintain a list of active squids.
   * A newly booted virtual machine will query the webserver and retrieve a json encoded string that contains the IP of the nearest squid server.

## Shoal-Server

- Service used for keeping track of squid servers, and providing a handy GUI webpage.

## Shoal-Agent

- Service used on squid servers. Sends an AMQP message to the shoal-server at a fixed interval set in the configuration.

## Shoal-Client

- Service used on worker nodes. Will retrieve a list of nearby squids which it can use.

##License

This program is free software; you can redistribute it and/or modify it under the terms of either:

a) the GNU General Public License as published by the Free Software Foundation; either version 3, or (at your option) any later version, or

b) the Apache v2 License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See either the GNU General Public License or the Apache v2 License for more details.

You should have received a copy of the Apache v2 License with this software, in the file named "LICENSE".

You should also have received a copy of the GNU General Public License along with this program in the file named "COPYING". If not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA or visit their web page on the internet at http://www.gnu.org/copyleft/gpl.html.
