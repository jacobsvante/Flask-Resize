import os
from contextlib import contextmanager

from . import constants, exc
from ._compat import redis


def make(config):
    """Generate cache store from supplied config

    Args:
        config (dict):
            The config to extract settings from

    Returns:
        Any[RedisCache, NoopCache]:
            A :class:`Cache` sub-class, based on the `RESIZE_CACHE_STORE`
            value.

    Raises:
        RuntimeError: If another `RESIZE_CACHE_STORE` value was set

    """
    if config.cache_store == 'redis':
        kw = dict(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            key=config.redis_key,
        )
        return RedisCache(**kw)
    elif config.cache_store == 'noop':
        return NoopCache()
    else:
        raise RuntimeError(
            'Non-supported RESIZE_CACHE_STORE value: "{}"'
            .format(config.cache_store)
        )


class Cache:
    """Cache base class"""

    def exists(self, unique_key):
        raise NotImplementedError

    def add(self, unique_key):
        raise NotImplementedError

    def remove(self, unique_key):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def all(self):
        raise NotImplementedError

    def transaction(self, unique_key, ttl=600):
        raise NotImplementedError


class NoopCache(Cache):
    """
    No-op cache, just to get the same API regardless of whether cache is
    used or not.
    """

    def exists(self, unique_key):
        """
        Check if key exists in cache

        Args:
            unique_key (str): Unique key to check for

        Returns:
            bool: Whether key exist in cache or not
        """
        return False

    def add(self, unique_key):
        """
        Add key to cache

        Args:
            unique_key (str): Add this key to the cache

        Returns:
            bool: Whether key was added or not
        """
        return False

    def remove(self, unique_key):
        """
        Remove key from cache

        Args:
            unique_key (str): Remove this key from the cache

        Returns:
            bool: Whether key was removed or not
        """
        return False

    def clear(self):
        """
        Remove all keys from cache

        Returns:
            bool: Whether any keys were removed or not
        """
        return False

    def all(self):
        """
        List all keys in cache

        Returns:
            List[str]: All the keys in the set, as a list
        """
        return []

    @contextmanager
    def transaction(self, unique_key, ttl=600):
        """
        No-op context-manager for transactions. Always yields `True`.
        """
        yield True


class RedisCache(Cache):
    """A Redis-based cache that works with a single set-type key

    Basically just useful for checking whether an expected value in the set
    already exists (which is exactly what's needed in Flask-Resize)
    """

    def __init__(
        self,
        host='localhost',
        port=6379,
        db=0,
        key=constants.DEFAULT_REDIS_KEY
    ):
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
        """
        Check if key exists in cache

        Args:
            unique_key (str): Unique key to check for

        Returns:
            bool: Whether key exist in cache or not
        """
        return self.redis.sismember(self.key, unique_key)

    def add(self, unique_key):
        """
        Add key to cache

        Args:
            unique_key (str): Add this key to the cache

        Returns:
            bool: Whether key was added or not
        """
        return bool(self.redis.sadd(self.key, unique_key))

    def remove(self, unique_key):
        """
        Remove key from cache

        Args:
            unique_key (str): Remove this key from the cache

        Returns:
            bool: Whether key was removed or not
        """
        return bool(self.redis.srem(self.key, unique_key))

    def clear(self):
        """
        Remove all keys from cache

        Returns:
            bool: Whether any keys were removed or not
        """
        return bool(self.redis.delete(self.key))

    def all(self):
        """
        List all keys in cache

        Returns:
            List[str]: All the keys in the set, as a list
        """
        return [v.decode() for v in self.redis.smembers(self.key)]

    @contextmanager
    def transaction(
        self,
        unique_key,
        ttl=600
    ):
        """
        Context-manager to use when it's important that no one else
        handles `unique_key` at the same time (for example when
        saving data to a storage backend).

        Args:
            unique_key (str):
                The unique key to ensure atomicity for
            ttl (int):
                Time before the transaction is deemed irrelevant and discarded
                from cache. Is only relevant if the host forcefully restarts.
        """
        tkey = '-transaction-'.join([self.key, unique_key])

        if self.redis.set(tkey, str(os.getpid()), nx=True):
            self.redis.expire(tkey, ttl)
        else:
            yield False

        try:
            yield True
        finally:
            self.redis.delete(tkey)
