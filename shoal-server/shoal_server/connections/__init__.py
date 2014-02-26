import redis
import rabbitmq

def setup_redis(settings):
    """Redis Connection"""
    return redis.StrictRedis(host=settings['redis']['host'],
                                   port=settings['redis']['port'],
                                   db=settings['redis']['db'])


def setup_rabbitmq(settings, shoal):
    return rabbitmq.Consumer(settings, shoal)
