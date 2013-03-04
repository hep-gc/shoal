#Shoal Agent v0.1

##How to install
1. Copy shoal-agent folder to `/usr/local/`
2. Copy the init script in the `bin/` directory to `/etc/init.d/`
3. Create/Move `shoal_agent.conf` to `/etc/shoal_agent.conf` and adjust settings.
4. If system supports it, `chkconfig --add shoal_agent` to start shoal agent on boot.

*Note: Requires python 2.6+.*

##Basic Commands
With the basic shoal_agent init script you can do the following:
- Start shoal_agent
 - `service shoal_agent start`
- Stop shoal_agent
 - `service shoal_agent stop` 
- Restart shoal_agent
 - `service shoal_agent reload` 
- Status of shoal_agent
 - `service shoal_agent status` 
- Force restart shoal_agent
 - `service shoal_agent force-restart` 
