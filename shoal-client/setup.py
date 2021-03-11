from __future__ import print_function
import os
from os.path import isfile, join
import sys
import shutil
import io
try:
    from setuptools import setup
except:
    try:
        from distutils.core import setup
    except:
        print("Couldn't use either setuptools or distutils. Install one of those.", file=sys.stderr)
        sys.exit(1)

from shoal_client.__version__ import version

try:
    with io.open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    print("Couldn't read description from the README.md", file=sys.stderr)
    long_description = ''

setup(name='shoal-client',
      version=version,
      license="'GPL3' or 'Apache 2'",
      install_requires=[
          'requests>=2.6.0',
          'netifaces>=0.10.0'
      ],
      description='A squid cache publishing and advertising tool designed to work in fast changing environments',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Mike Chester, Colson Drimiel, Ian Gable, Alex Lam, Rob Prior, Ryan Taylor, Steve Traylen, Marcus Ebert, Da Meng',
      author_email='heprc-shoal@uvic.ca',
      url='http://github.com/hep-gc/shoal',
      packages=['shoal_client'],
      scripts=['shoal-client'],
      data_files=[('share/shoal-client', ['conf/shoal_client.conf'])],
)

