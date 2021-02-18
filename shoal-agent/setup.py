import os
from os.path import isfile, join, expanduser
import sys
import io
try:
    from setuptools import setup
except:
    try:
        from distutils.core import setup
    except:
        print("Couldn't use either setuptools or distutils. Install one of those.")
        sys.exit(1)

from shoal_agent.__version__ import version

try:
    with io.open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except: 
    print("Couldn't read description from the README.md")
    long_description = ''

setup(name='shoal-agent',
      version=version,
      license="'GPL3' or 'Apache 2'",
      install_requires=[
          'netifaces>=0.5',
          'pika>=0.9.5',
          'pystun3>=1.0.0',
          'requests>=2.6.0',
      ],
      description='A squid cache publishing and advertising tool designed to work in fast changing environments',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Mike Chester, Colson Drimiel, Ian Gable, Alex Lam, Rob Prior, Ryan Taylor, Steve Traylen, Marcus Ebert, Da Meng',
      author_email='heprc-shoal@uvic.ca',
      url='http://github.com/hep-gc/shoal',
      packages=['shoal_agent'],
      scripts=['shoal-agent','shoal-agent-installation.sh'],
      data_files=[('share/shoal-agent', ['conf/shoal_agent.conf','conf/shoal-agent.init','conf/shoal-agent.logrotate','conf/shoal-agent.service'])],
      options = {'bdist_rpm':{'requires':'python-netifaces >= 0.5,python-pika >= 0.9.5'}},
)
