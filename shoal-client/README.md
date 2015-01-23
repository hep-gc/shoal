#Shoal Client v0.5.X README

shoal-client will configure cvmfs to use the closest squid server to you by contacting the shoal server
and then editing your local cvmfs config file, typically `/etc/cvmfs/default.local`.

shoal-client is a simple python script typically configured to run with cron to check for new squids 
periodically. Before setting the cronjob in place make sure that shoal-client is
configured correctly (see Usage below).

##Installation

**Note**: Requires Python 2.4+

**Note**: Shoal config files will be located either at `~/.shoal/` or `/etc/shoal/` if installed 
root permissions.

###Recommended Instalation Method: Use yum

First install [EPEL](http://fedoraproject.org/wiki/EPEL)

    sudo yum install yum-conf-epel
    sudo yum update

Get the Shoal yum repository:

    sudo curl http://shoal.heprc.uvic.ca/repo/shoal.repo -o /etc/yum.repos.d/shoal.repo
   
Install the agent:

    sudo yum install shoal-client

Configure the client to use a shoal server:

    vim /etc/shoal/shoal_client.conf
    If you are using a shoal sever that has verification enabled make sure the configuration is set to the verifiednearest URL
    
##Usage

Confirm the that you configured shoal-client as expected by checking the output of `shoal-client --dump`
This is what will be written to `/etc/cvmfs/default.local` when you run `shoal-client`. For example you will see 
something like the following:

<pre>
CVMFS_REPOSITORIES=atlas.cern.ch,atlas-condb.cern.ch,atlas-nightlies.cern.ch,sft.cern.ch
CVMFS_QUOTA_LIMIT=10000
CVMFS_HTTP_PROXY="[[DYNAMIC SQUID HOSTNAMES APPENDED HERE]];http://chrysaor.westgrid.ca:3128;http://cernvm-webfs.atlas-canada.ca:3128;DIRECT"
</pre>

If the output looks resonable now set a crontab entry to run shoal say every 30 minutes:

    crontab -e
    0,30 * * * * /usr/bin/shoal-client



### Hint for the ATLAS Experiment Users:

A complete shoal_client.conf file for ATLAS can be obtained by:

    sudo curl http://shoal.heprc.uvic.ca/repo/shoal_client.conf -o /etc/shoal/shoal_client.conf


## Other Installation Methods

###Using Pip

1. `pip install shoal-client`
2. Check settings in `shoal_client.conf` update as needed.

###Using Git
1. `git clone git://github.com/hep-gc/shoal.git`
2. `cd shoal/shoal-client/`
3. `python setup.py install`
4. Check settings in `shoal_client.conf` update as needed

