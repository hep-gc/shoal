# Shoal Client README
# Version: v0.6.X

shoal-client will configure cvmfs to use the closest squid server to you by contacting the shoal server
and using cvfms-talk to update the active proxy configuration.

shoal-client is a simple python script typically configured to run with cron to check for new squids 
periodically. Before setting the cronjob in place make sure that shoal-client is
configured correctly (see Usage below).

With the release of v0.6.4 the shoal-client now offers support for frontier. Running the shoal-client
with the --frontier or -f option will produce an output string instead of attempting to update the
proxies via cvmfs-talk. See Usage below for more information.


## Installation

**Note**: Requires Python 2.4+

**Note**: Shoal config files will be located either at `~/.shoal/` or `/etc/shoal/` if installed 
root permissions.

### Recommended Instalation Method: Use yum (est. ~5 min)

First install [EPEL](http://fedoraproject.org/wiki/EPEL) 

    sudo yum install epel-release
    sudo yum update

Get the Shoal yum repository:

    For SL6:
    sudo curl http://shoal.heprc.uvic.ca/repo/shoal-sl6x.repo -o /etc/yum.repos.d/shoal.repo

    For SL7:
    sudo curl http://shoal.heprc.uvic.ca/repo/shoal-sl7x.repo -o /etc/yum.repos.d/shoal.repo
   
Install the agent:

	sudo rpm --import http://shoal.heprc.uvic.ca/repo/pubkeys/heprc.asc
    sudo yum install shoal-client

Configure the client to use a shoal server:

    vim /etc/shoal/shoal_client.conf

If you are using a shoal sever that has verification enabled make sure the configuration is set to
the verifiednearest URL


### Hint for the ATLAS Experiment Users:

A complete shoal_client.conf file for ATLAS can be obtained by:

    sudo curl http://shoal.heprc.uvic.ca/repo/shoal_client.conf -o /etc/shoal/shoal_client.conf

    
## Usage

Confirm the that you configured shoal-client as expected by checking the output of `shoal-client --dump`
The output is a list of servers that will be set as proxies using cvfms-talk. For example you will see 
something like the following:
`http://squid.example1.com:3128;http://squid.example2.com:3128;http://squid.example3.com:3128;http://squid.example4.com:3128;http://squid.example5.org:3128;DIRECT`

If the output looks resonable now set a crontab entry to run shoal say every 30 minutes:

    crontab -e
    0,30 * * * * /usr/bin/shoal-client

New in version 0.6.4 is the --frontier option that will produce an output string suitable for frontier.
Users will need to use a simple script that runs shoal-client and uses the output to set the proxies.
An example script can be found [here](https://github.com/hep-gc/shoal/blob/master/shoal-client/scripts/frontier_set.sh) in the shoal-client/scripts directory.
Example output when running `shoal-client --frontier`:
`(serverurl=http://PresetServer.ca:3128)(proxyurl=http://PROXY.FROM.SHOAL.1:3128)(proxyurl=http://PROXY.FROM.SHOAL.2:3128)`

## Other Installation Methods

###Using Pip

1. `pip install shoal-client`
2. Check settings in `shoal_client.conf` update as needed.

###Using Git
1. `git clone git://github.com/hep-gc/shoal.git`
2. `cd shoal/shoal-client/`
3. `python setup.py install`
4. Check settings in `shoal_client.conf` update as needed

