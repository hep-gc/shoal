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
        print("Couldn't use either setuptools or distutils. Install one of those.")
        sys.exit(1)

from shoal_client.__version__ import version

try:
    with io.open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    print("Couldn't read description from the README.md")
    long_description = ''

def postInstallation():
    try:
        if os.path.isfile('/etc/shoal/shoal_client.conf'):
            src="conf/shoal_client.conf"
            dst="/etc/shoal/shoal_client_new.conf"
            shutil.copy(src,dst)
        else:
            if not os.path.isdir('/etc/shoal'):
                os.makedirs('/etc/shoal')
            src="conf/shoal_client.conf"
            dst="/etc/shoal/shoal_client.conf"
            shutil.copy(src,dst)
    except Exception as exc:
        print(exc)
        print('Could not auto copy the configuration file to the path /etc/shoal/, please review and copy it from /usr/share/shoal-client/ manually if you need')

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

postInstallation()
