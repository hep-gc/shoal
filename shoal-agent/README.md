# Shoal Agent README
# Version: v1.0.0


## Important to know about the configuration
The configuration has been simplified compared to previous versions and most settings are automatically configured at runtime.


## Basic Commands
With the basic `shoal_agent` init script you can do the following:

```
service shoal-agent start
service shoal-agent stop
service shoal-agent reload 
service shoal-agent status
service shoal-agent force-restart
```

## Installation

The **recommended** way to install is with pip.
The Shoal agent does not require root privilege to run; by default the `shoal` user and group is used. If the shoal user and group do not exist then the install script will create the entries in the system.

 _**Note**: Requires you have Python 2.6+, and the pika python module (available from EPEL)._

### Recommended Method: Use pip (est. ~5 min)
  1. Login as root or become root via `sudo su -`
  2. Install shoal-agent using pip/pip3, e.g. `pip3 install shoal-agent`
  3. Run the installation script, `shoal-agent-installation.sh`, to setup your configuration
  
  

