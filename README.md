# Shoal v0.1 README
A squid cache publishing and advertising tool designed to work in fast changing environments.

## Overview

   * Each squid server will send an AMQP json encoded message to a centralized RabbitMQ server queue.
   * A webserver will retrieve the messages from the queue and maintain a list of active squids.
   * A newly booted virtual machine will query the webserver via a RESTful API to retrieve the ip of the nearest squid server.

### How to Install
    
More information coming soon...

### Basic configurations

More information coming soon...

### How to run

More information coming soon...

### LICENSE
