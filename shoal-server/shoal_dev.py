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
    threads.append(shoal_thread)

    webpy_app = shoal.WebpyServer(shoal_list)
    webpy_thread = Thread(target=webpy_app.run(), name='Webpy')
    webpy_thread.daemon = True
    threads.append(webpy_thread)

    for thread in threads:
        thread.start()

    try:
        while True:
            for thread in threads:
                if not thread.is_alive():
                    logging.error('{0} died.'.format(thread))
                    sys.exit()
            sleep(1)
    except KeyboardInterrupt:
        sys.exit()


if __name__ == '__main__':
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
