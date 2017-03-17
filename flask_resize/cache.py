from . import constants, exc
from ._compat import redis


class Cache:

    def exists(self, unique_key):
        raise NotImplementedError

    def add(self, unique_key):
        raise NotImplementedError

    def remove(self, unique_key):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class NoopCache(Cache):

    def exists(self, unique_key):
        return False

    def add(self, unique_key):
        pass

    def remove(self, unique_key):
        pass

    def clear(self, unique_key):
        pass


class RedisCache(Cache):

    def __init__(self, host='localhost', port=6379, db=0, key=constants.DEFAULT_REDIS_KEY):
        if redis is None:
            raise exc.RedisImportError(
                "Redis must be installed for Redis support. "
                "Package found @ https://pypi.python.org/pypi/redis."
            )
        self.host = host
        self.port = port
        self.db = db
        self.key = key
        self.redis = redis.StrictRedis(host=host, port=port, db=db)

    def exists(self, unique_key):
        return self.redis.sismember(self.key, unique_key)

    def add(self, unique_key):
        return self.redis.sadd(self.key, unique_key)

    def remove(self, unique_key):
        return self.redis.srem(self.key, unique_key)

    def clear(self):
        return self.redis.delete(self.key)
