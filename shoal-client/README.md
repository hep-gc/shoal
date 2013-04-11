#Shoal Client v0.4.X README

##Basic Usage

- After installing and before deploying Shoal Client, confirm the output will be what you expect. It should look like the following formatted text. `shoal-client --dump` will print the contents of `default.local` to stdout.

    <pre>
VMFS_REPOSITORIES=atlas.cern.ch,atlas-condb.cern.ch,grid.cern.ch
CVMFS_QUOTA_LIMIT=3500
CVMFS_HTTP_PROXY="[[DYNAMIC SQUID HOSTNAMES APPENDED HERE]];http://chrysaor.westgrid.ca:3128;http://cernvm-webfs.atlas-canada.ca:3128;DIRECT"
    </pre>

- Because of how CVMFS operates at the current time of this writing, it is necessary to update the default.local file before accessing CVMFS files. It is recommended to run Shoal Client on boot.

##Installation

 _**Note**: Requires Python 2.4+_

_**Note**: Shoal config files will be located either at `~/.shoal/` or `/etc/shoal/` if sudo was used_

###Using Pip

1. `pip install shoal-client`
2. Check settings in `shoal_client.conf` update as needed.

###Using Git
1. `git clone git://github.com/hep-gc/shoal.git`
2. `cd shoal/shoal-client/`
3. `python setup.py install`
4. Check settings in `shoal_client.conf` update as needed
