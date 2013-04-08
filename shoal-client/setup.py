import os
from os.path import isfile, join
import sys
try:
    from setuptools import setup
except:
    try:
        from distutils.core import setup
    except:
        print "Couldn't use either setuputils or distutils. Install one of those."
        sys.exit(1)

from shoal_client.__version__ import version

if not os.geteuid() == 0:
    config_files_dir = os.path.expanduser("~/.shoal/")
else:
    config_files_dir = "/etc/shoal/"
    #initd_dir = "/etc/init.d/"
    #initd_script = "scripts/shoal_client"

    # check for preexisiting initd script
    #if not isfile(join(initd_dir, initd_script)):
    #    data_files += [(initd_dir, [initd_script])]

config_file = "shoal_client.conf"

data_files = []

# check for preexisting config files
if not isfile(join(config_files_dir, config_file)):
    data_files += [(config_files_dir, [config_file])]

setup(name='shoal-client',
      version=version,
      license="'GPL3' or 'Apache 2'",
      install_requires=[],
      description='A squid cache publishing and advertising tool designed to work in fast changing environments',
      author='Mike Chester',
      author_email='mchester@uvic.ca',
      url='http://github.com/hep-gc/shoal',
      packages=['shoal_client'],
      scripts=['shoal-client'],
      data_files=data_files,
)
