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
        print ("Couldn't use either setuputils or distutils. Install one of those.")
        sys.exit(1)

from shoal_server.__version__ import version


setup(name='shoal-server',
      version=version,
      license="'GPL3' or 'Apache 2'",
      install_requires=[
          'pygeoip>=0.2.5',
          'pika>=0.9.11',
          'web.py>=0.61',
          'requests>=2.3.0',
          'geoip2>=0.6.0',
          'maxminddb>=1.1.1',
          'ipaddr>=2.1.9',
      ],
      description='A cache cache publishing and advertising tool designed to work in fast changing environments',
      author='Mike Chester, Colson Drimiel, Ian Gable, Alex Lam, Rob Prior, Ryan Taylor, Marcus Ebert, Da Meng, Seojin Lee',
      author_email='heprc-shoal@uvic.ca',
      url='http://github.com/hep-gc/shoal',
      packages=['shoal_server'],
      scripts=["shoal-server"],
      data_files=[('share/shoal-server', ['conf/shoal_server.conf', 'conf/shoal.conf','conf/shoal-server.logrotate']),
                       ('share/shoal-server/scripts', ['conf/scripts/shoal_wsgi.py']),
                       ('share/shoal-server/static/img', ['static/img/glyphicons-halflings.png','static/img/glyphicons-halflings-white.png']),
                       ('share/shoal-server/static/img/icons', ['static/img/icons/favicon.ico',]),
                       ('share/shoal-server/templates', ['templates/base.html','templates/index.html','templates/wpad.dat'])                 
                   ],
#      options = {'bdist_rpm':{'post_install':'manage_permissions'}},
)
