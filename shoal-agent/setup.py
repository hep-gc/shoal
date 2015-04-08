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

    
setup(name='shoal-agent',
      version=version,
      license="'GPL3' or 'Apache 2'",
      install_requires=[
          'netifaces>=0.5',
          'pika>=0.9.5',
      ],
      description='A squid cache publishing and advertising tool designed to work in fast changing environments',
      author='Mike Chester, Colson Drimiel, Ian Gable, Alex Lam, Rob Prior, Ryan Taylor, Steve Traylen',
      author_email='igable@uvic.ca',
      url='http://github.com/hep-gc/shoal',
      packages=['shoal_agent'],
      scripts=['shoal-agent'],
      data_files=[('share/shoal-agent', ['conf/shoal_agent.conf','conf/shoal-agent.init','conf/shoal-agent.logrotate','conf/shoal-agent.sysconfig','conf/shoal-agent.service'])
                  ],
      options = {'bdist_rpm':{'post_install':'manage_permissions'},
                 'bdist_rpm':{'requires':'python-netifaces >= 0.5,python-pika >= 0.9.5'}},
)
