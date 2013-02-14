from setuptools import setup

setup(name='shoal',
      version='0.1',
      description='A squid cache publishing and advertising tool designed to work in fast changing environments',
      url='http://github.com/hepgc/shoal',
      author='Mike Chester',
      author_email='mchester@uvic.ca',
      license='MIT',
      packages['shoal'],
      istall_requires=[
          'pygeoip',
          'pika',
          'webpy',
      ],
      zip_safe=False)
