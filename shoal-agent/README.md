#Shoal Agent v0.6.X README

##Basic Commands
With the basic `shoal_agent` init script you can do the following:
- Start Shoal Agent
 - `service shoal_agent start`
- Stop Shoal Agent
 - `service shoal_agent stop` 
- Restart Shoal Agent
 - `service shoal_agent reload` 
- Status of Shoal Agent
 - `service shoal_agent status` 
- Force restart Shoal Agent
 - `service shoal_agent force-restart`

##Installation

 _**Note**: Requires you have a working RabbitMQ AMQP Server, and Python 2.6+_

_**Note**: Shoal config files will be located either at `~/.shoal/` or `/etc/shoal/` if sudo was used_

###Using Pip

1. `pip install shoal-agent`
2. Check settings in `shoal_agent.conf` update as needed. Make sure RabbitMQ server is running.
3. If sudo was used `chmod +x /etc/init.d/shoal_agent`.
 - May need to adjust values in init.d script to point at `shoal-agent` script and usable Python path.

4. Start Shoal Agent `service shoal_agent start` or `shoal-agent` and confirm it works.
5. Add Shoal Agent to chkconfig or similiar service. 
 - `chkconfig --add shoal_agent`
 - `chkconfig shoal_agent on` 

###Using Git
1. `git clone git://github.com/hep-gc/shoal.git`
2. `cd shoal/shoal-agent/`
3. `python setup.py install`
4. Adjust config file located at `/etc/shoal/shoal_agent.conf` or `~/.shoal/shoal_agent.conf`
5. Confirm `shoal-agent` runs.
6. Add Shoal Agent to chkconfig or similiar service. 
 - `chkconfig --add shoal_agent`
 - `chkconfig shoal_agent on`
