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


setup(name='shoal-client',
      version=version,
      license="'GPL3' or 'Apache 2'",
      install_requires=[],
      description='A squid cache publishing and advertising tool designed to work in fast changing environments',
      author='Mike Chester, Colson Drimiel, Ian Gable, Alex Lam, Rob Prior, Ryan Taylor, Steve Traylen',
      author_email='igable@uvic.ca',
      url='http://github.com/hep-gc/shoal',
      packages=['shoal_client'],
      scripts=['shoal-client'],
      data_files=[('share/shoal-client', ['conf/shoal_client.conf'])
                  ],
)
