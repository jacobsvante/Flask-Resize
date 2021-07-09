import logging
import os
import uuid

import pytest
from PIL import Image

import flask_resize
from flask_resize import _compat, resizing


logging.basicConfig(format="%(levelname)s:%(name)s:%(thread)d:%(message)s")
log_level = os.environ.get("RESIZE_LOG_LEVEL", "error")
flask_resize.logger.setLevel(getattr(logging, log_level.upper()))


def pytest_addoption(parser):
    parser.addoption(
        "--skip-slow",
        action="store_true",
        help="Skip slow-running tests",
    )


@pytest.fixture
def image1():
    return Image.new("RGB", (512, 512), "red")


@pytest.fixture
def image1_data(image1):
    return resizing.image_data(image1, "PNG")


@pytest.fixture
def image1_name():
    return "flask-resize-test-{}.png".format(uuid.uuid4().hex)


@pytest.fixture
def image1_key(image1_name, resizetarget_opts):
    target = resizing.ResizeTarget(**resizetarget_opts)
    # Obviously only the key if no processing settings have been pas
    return target.unique_key


@pytest.fixture
def image2():
    return Image.new("RGB", (512, 512), "blue")


@pytest.fixture
def image2_data(image2):
    return resizing.image_data(image2, "PNG")


@pytest.fixture
def filestorage(tmpdir):
    return flask_resize.storage.FileStorage(base_path=str(tmpdir))


@pytest.fixture
def redis_cache():
    if _compat.redis:
        cache_store = flask_resize.cache.RedisCache(
            host=os.environ.get("REDIS_HOST", "localhost"),
            key="flask-resize-redis-test-{}".format(uuid.uuid4().hex),
        )
    else:

        class FakeRedis:
            key = None
            _host = None

        # NOTE: Won't be used as long as @tests.decorators.requires_redis
        #       is used.
        cache_store = FakeRedis()

    yield cache_store

    if _compat.redis:
        cache_store.clear()


@pytest.fixture
def resizetarget_opts(filestorage, image1_name):
    return dict(
        image_store=filestorage,
        source_image_relative_url=image1_name,
        dimensions="100x50",
        format="jpeg",
        quality=80,
        fill=False,
        bgcolor=None,
        upscale=True,
        progressive=True,
        use_placeholder=False,
        cache_store=flask_resize.cache.NoopCache(),
    )
