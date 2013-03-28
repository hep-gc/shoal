import logging
import sys
import os

from shoal_server import shoal as shoal
from shoal_server import config as config
from threading import Thread
from time import sleep

config.setup()

DIRECTORY = config.shoal_dir
LOG_FILE = config.log_file
LOG_FORMAT = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)s] - %(message)s'

threads = []
shoal_list = {}

def main():
    shoal_app = shoal.Application(shoal_list)
    shoal_thread = Thread(target=shoal_app.run(), name='ShoalServer')
    shoal_thread.daemon = True
    shoal_thread.start()

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

main()
webpy_app = shoal.WebpyServer(shoal_list)
application = webpy_app.wsgi()
