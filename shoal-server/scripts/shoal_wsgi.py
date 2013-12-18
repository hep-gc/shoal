import logging
import sys
import os

from shoal_server import config as config

from shoal_server import shoal as shoal
from threading import Thread
from time import sleep


DIRECTORY = config.shoal_dir
LOG_FILE = config.log_file
LOG_FORMAT = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)s] - %(message)s'

threads = []
shoal_list = {}

try:
    logging.basicConfig(level=logging.ERROR, format=LOG_FORMAT, filename=LOG_FILE)
except IOError as e:
    print "Could not set logger.", e
    sys.exit(1)

# change working directory so webpy static files load correctly.
try:
    os.chdir(DIRECTORY)
except OSError as e:
    print "{0} doesn't seem to exist. Please set `shoal_dir` in shoal-server config file to the location of the shoal-server static files.".format(DIRECTORY)
    sys.exit(1)

monitor_thread = shoal.ThreadMonitor(shoal_list)
monitor_thread.daemon = True
monitor_thread.start()

webpy_app = shoal.WebpyServer(shoal_list)
application = webpy_app.wsgi()
