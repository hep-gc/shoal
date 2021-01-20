# Shoal Agent README
# Version: v1.0.X


## Important to know about the configuration
There a 3 possible configurations:
* local
* private
* global   

local and private modes usable when a squid is only for own machines, e.g. VMs on an own cloud. The difference is that for "private" the squid function will not be verified by the shoal server, while for "local" it would. Both would only be given to a shoal-client running in the same subnet.   
When a squid is configured as global, then it must be accessible by the shoal-server or it can not be verified. Unverified global squids will not be given out to any shoal client!

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

The **best** way to install is with pip. The impatient should skip to the Recommended Method section below.

In either case, the Shoal agent does not require root privilege to run. The init script uses the `nobody` user by default, although this is adjustable.

 _**Note**: Requires you have Python 2.6+, and the pika python module (available from EPEL)._

### Recommended Method: Use pip (est. ~5 min)
  1. Install python library: `pip install shoal-agent`
  2. Move configuration files from `/usr/share/shoal-agent/` to their proper locations:
  * `/usr/share/shoal-agent/shoal_agent.conf` --> `/etc/shoal/shoal_agent.conf`
  * `/usr/share/shoal-agent/shoal-agent.init` --> `/etc/init.d/shoal-agent`
  * `/usr/share/shoal-agent/shoal-agent.logrotate` --> `/etc/logrotate.d/shoal-agent`
  * `/usr/share/shoal-agent/shoal-agent.sysconfig` --> `/etc/sysconfig/shoal/shoal-agent`
  * `/usr/share/shoal-agent/shoal-agent.service` --> `/usr/lib/systemd/system/shoal-agent.service` (if necessary)
  3. Modify the settings in `shoal_agent.conf` as needed.
  5. Create the user and group `shoal`
  6. Create a log file for shoal `/var/log/shoal_agent.log` owned by `shoal:shoal` with `0644`
  4. Start shoal agent: `service shoal-agent start`
  
  

