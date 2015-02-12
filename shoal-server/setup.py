import os
from os.path import join, isfile, expanduser
import os.path
import sys
try:
    from setuptools import setup
except:
    try:
        from distutils.core import setup
    except:
        print "Couldn't use either setuputils or distutils. Install one of those."
        sys.exit(1)

from shoal_server.__version__ import version


data_files = []

if not os.geteuid() == 0:
    config_files_dir = expanduser('~/.shoal/')
    shoal_server_dir = expanduser('~/shoal_server')
else:
    config_files_dir = "/etc/shoal/"
    shoal_server_dir = "/var/shoal/"

static_files_dir = "static/"
script_files_dir = "scripts/"
template_files_dir = "templates/"
config_file = "shoal_server.conf"

# Recursively include all files in src, and create them in dst if they don't exist
def include_files(src, dst):
    temp = []
    for subdir, dirs, files in os.walk(src):
        f = []
        path = join(dst, subdir)
        for file in files:
            if not isfile(join(path, file)):
                f.append(join(subdir, file))
        if f:
            temp.append((path, f))
    return temp

# check for preexisting config files
if not isfile(join(config_files_dir, config_file)):
    data_files += [(config_files_dir, [config_file])]
# add all files in static/
data_files += include_files(static_files_dir, shoal_server_dir)
# add all files in templates/
data_files += include_files(template_files_dir, shoal_server_dir)
# add all files in scripts/
data_files += include_files(script_files_dir, shoal_server_dir)

setup(name='shoal-server',
      version=version,
      license="'GPL3' or 'Apache 2'",
      install_requires=[
          'pygeoip>=0.2.5',
          'pika>=0.9.11',
          'web.py>=0.3',
          'python-requests>=1.1.0',
          'geoip2>=0.6.0',
          'maxminddb>=1.1.1',
          
      ],
      description='A squid cache publishing and advertising tool designed to work in fast changing environments',
      author='Mike Chester',
      author_email='mchester@uvic.ca',
      url='http://github.com/hep-gc/shoal',
      packages=['shoal_server'],
      scripts=["shoal-server"],
      data_files=data_files,
)
