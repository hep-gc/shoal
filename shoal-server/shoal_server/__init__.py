import logging
import config
import signal
import time
import tornado.ioloop

from application import Application

def shutdown():
    max_wait = 3

    io_loop = tornado.ioloop.IOLoop.instance()
    logging.info("Shutting down Tornado IOLoop in %s seconds...", max_wait)

    deadline = time.time() + max_wait

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            logging.info("Shutdown.")
    stop_loop()

def signal_handler(sig, frame):
    logging.warning("Caught signal: %s", sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)

def run():
    # setup signal handling
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    io_loop = tornado.ioloop.IOLoop.instance()

    app = Application(config.settings, io_loop)

    # Hook RabbitMQ consumer into Tornado IOLoop
    logging.info("Hooking RabbitMQ Consumer into IOLoop...")
    io_loop.add_timeout(time.time() + .1, app.rabbitmq.run)
    logging.info("complete.")

    logging.info("Starting Tornado on Port %s", config.settings['tornado']['port'])
    app.listen(config.settings['tornado']['port'])

    io_loop.start()
