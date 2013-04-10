# Shoal-Client v0.4.X README

##Installation
_Requires python 2.4+_
###Easy Way

1. Use `pip`
   - `pip install shoal-client`

2. Location of files depending if **sudo** was used or not 
  1. **Configuration Files:** `/etc/shoal/shoal_client.conf`
  2. Configuration Files: `~/.shoal/shoal_client.conf`
  - Set `shoal_server_url` to the REST API on Shoal-Server.
  - Set `cvmfs_config` to the cvmfs `default.local` file.
  - Set `default_squid_proxy` to fall back squids in case the dynamic squid is taken offline.


3. Confirm shoal-client will output the correct `default.local` file using `shoal-client --dump` should look similar to the following, with the dynamic squids being appended to the front of `CVMFS_HTTP_PROXY`:
    <pre>
VMFS_REPOSITORIES=atlas.cern.ch,atlas-condb.cern.ch,grid.cern.ch
CVMFS_QUOTA_LIMIT=3500
CVMFS_HTTP_PROXY="[[DYNAMIC SQUID HOSTNAMES]];http://chrysaor.westgrid.ca:3128;http://cernvm-webfs.atlas-canada.ca:3128;DIRECT"
    </pre>

4. Add shoal-client to `/etc/rc.local` (or other script run on boot).
  - `/path/to/shoal-client`

###Hard Way
1. Copy shoal-client folder to any working directory.
2. Adjust .conf file included, and place in `/etc/`.
3. Run `shoal_client.py`
