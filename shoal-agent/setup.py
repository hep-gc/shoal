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

from setuptools import setup
from shoal_agent.__version__ import version

config_files_dir = "/etc/shoal/"
initd_dir = "/etc/init.d/"
initd_script = "scripts/shoal_agent"
config_file = "shoal_agent.conf"

data_files = []

# check for preexisting config files
if not isfile(join(config_files_dir, config_file)):
    data_files += [(config_files_dir, [config_file])]
# check for preexisiting initd script
if not isfile(join(initd_dir, initd_script)):
    data_files += [(initd_dir, [initd_script])]

setup(name='shoal-agent',
      version=version,
      license='GPL3' or 'Apache 2',
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
