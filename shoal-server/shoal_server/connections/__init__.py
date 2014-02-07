import redis
import rabbitmq

def setup_redis(settings):
    """Redis Connection"""
    return redis.StrictRedis(host=settings['redis']['host']['value'],
                                   port=settings['redis']['port']['value'],
                                   db=settings['redis']['db']['value'])


def setup_rabbitmq(settings, io_loop):
    return rabbitmq.Consumer(settings, io_loop)


def setup(settings, io_loop):
    conn = dict()
    conn['redis'] = setup_redis(settings)
    conn['rabbitmq'] = setup_rabbitmq(settings, io_loop)
    return conn
