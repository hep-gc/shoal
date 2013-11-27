import os
from os.path import isfile, join, expanduser
import sys
try:
    from setuptools import setup
except:
    try:
        from distutils.core import setup
    except:
        print "Couldn't use either setuputils or distutils. Install one of those."
        sys.exit(1)

from shoal_agent.__version__ import version

data_files = []

if not os.geteuid() == 0:
    config_files_dir = expanduser("~/.shoal/")
else:
    config_files_dir = "/etc/shoal/"
    # if root install the init.d scripts.
    # check for preexisiting initd script
    initd_dir = "/etc/init.d/"
    initd_script = "scripts/shoal-agent"
    if not isfile(initd_dir + "shoal-agent"):
        data_files += [(initd_dir, [initd_script])]

config_file = "shoal_agent.conf"

# check for preexisting config files
if not isfile(join(config_files_dir, config_file)):
    data_files += [(config_files_dir, [config_file])]

setup(name='shoal-agent',
      version=version,
      license="'GPL3' or 'Apache 2'",
      install_requires=[
          'netifaces>=0.8',
          'pika>=0.9.9',
      ],
      description='A squid cache publishing and advertising tool designed to work in fast changing environments',
      author='Mike Chester',
      author_email='mchester@uvic.ca',
      url='http://github.com/hep-gc/shoal',
      packages=['shoal_agent'],
      scripts=['shoal-agent'],
      data_files=data_files,
)
