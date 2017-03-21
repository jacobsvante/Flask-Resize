from . import constants
from ._compat import redis


class Config:
    """The main configuration entry point"""

    url = None
    noop = False
    root = None
    raise_on_generate_in_progress = False
    storage_backend = 'file'
    target_directory = constants.DEFAULT_TARGET_DIRECTORY
    hash_method = constants.DEFAULT_NAME_HASHING_METHOD
    cache_store = 'noop' if redis is None else 'redis'
    redis_host = 'localhost'
    redis_port = 6379
    redis_db = 0
    redis_key = constants.DEFAULT_REDIS_KEY
    s3_access_key = None
    s3_secret_key = None
    s3_bucket = None
    s3_region = None

    def __init__(self, **config):
        for key, val in config.items():
            setattr(self, key, val)

    @classmethod
    def from_dict(cls, dct, default_overrides=None):
        """
        Turns a dictionary with `RESIZE_` prefix config options into lower-case
        keys on this object.

        Args:
            dct (dict):
                The dictionary to get explicitly set values from

            default_overrides (Any[dict,None]):
                A dictionary with default overrides, where all declared keys'
                values will be used as defaults instead of the "app default",
                in case a setting wasn't explicitly added to config.

        """
        prefix = 'RESIZE_'
        default_overrides = default_overrides or {}
        config = cls()

        def format_key(k):
            return k.split(prefix, 1)[1].lower()

        for key, val in dict(default_overrides, **dct).items():
            if key.startswith(prefix):
                setattr(config, format_key(key), val)

        return config

    @classmethod
    def from_pyfile(cls, filepath):
        conf = {}
        with open(filepath) as config_file:
            exec(compile(config_file.read(), filepath, 'exec'), conf)
        return cls.from_dict(conf)
