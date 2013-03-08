import os
import os.path
import sys
try:
    from setuptools import setup
except:
    try:
        from distutils.core import setup
    except:
        print "Couldn't use either setuputils or distutils. Install one of those. :)"
        sys.exit(1)

from setuptools import setup
from shoal_server.__version__ import version

config_files_dir = "/etc/shoal/"
config_files = ["shoal_server.conf"]

# check for preexisting config files
data_files = okay_files = []
for config_file in config_files:
    if not os.path.isfile(config_files_dir + os.path.basename(config_file)):
        okay_files.append(config_file)
if okay_files:
    data_files = [(config_files_dir, okay_files)]


setup(name='shoal-server',
      version=version,
      license='GPL3' or 'Apache 2',
      install_requires=[
          'pygeoip>=0.2.5',
          'pika>=0.9.9',
          'webpy>=0.3',
      ],
      description='A squid cache publishing and advertising tool designed to work in fast changing environments',
      author='Mike Chester',
      author_email='mchester@uvic.ca',
      url='http://github.com/hepgc/shoal',
      packages['shoal-server'],
      data_files = data_files,
)
