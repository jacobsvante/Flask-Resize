import os
import subprocess

import pytest

import flask_resize

from .decorators import requires_redis, slow


@pytest.fixture
def env(tmpdir, redis_cache):
    basedir = tmpdir
    conffile = tmpdir.join('flask-resize-conf.py')
    conffile.write(
        """
RESIZE_URL = 'https://example.com'
RESIZE_ROOT = '{root}'
RESIZE_REDIS_KEY = '{cache_key}'
        """
        .format(
            root=str(basedir).replace('\\', '\\\\'),
            cache_key=redis_cache.key,
        ).strip()
    )
    env = os.environ.copy()
    # env = dict(PATH=os.environ['PATH'])
    env.update(FLASK_RESIZE_CONF=str(conffile))
    return env


def run(env, *args):
    return subprocess.check_output(args, env=env).decode().splitlines()


@slow
def test_bin_usage(env):
    assert 'usage: flask-resize' in run(env, 'flask-resize', '--help')[0]


@slow
def test_bin_list_images_empty(env):
    assert run(env, 'flask-resize', 'list', 'images') == []


@slow
def test_bin_list_has_images(
    env,
    resizetarget_opts,
    image1_name,
    image1_data,
    image1_key
):
    resize_target = flask_resize.ResizeTarget(**resizetarget_opts)

    resize_target.image_store.save(image1_name, image1_data)
    resize_target.generate()
    assert run(env, 'flask-resize', 'list', 'images') == [image1_key]


@requires_redis
@slow
def test_bin_list_cache_empty(env, redis_cache):
    assert run(env, 'flask-resize', 'list', 'cache') == []


@requires_redis
@slow
def test_bin_list_has_cache(env, redis_cache):
    redis_cache.add('hello')
    redis_cache.add('buh-bye')
    assert set(run(env, 'flask-resize', 'list', 'cache')) == \
        {'hello', 'buh-bye'}


@slow
def test_bin_clear_images(
    env,
    resizetarget_opts,
    image1_name,
    image1_data
):
    resize_target = flask_resize.ResizeTarget(**resizetarget_opts)

    resize_target.image_store.save(image1_name, image1_data)
    resize_target.generate()
    run(env, 'flask-resize', 'clear', 'images')
    assert run(env, 'flask-resize', 'list', 'images') == []


@requires_redis
@slow
def test_bin_clear_cache(env, redis_cache):
    redis_cache.add('foo bar')
    assert run(env, 'flask-resize', 'clear', 'cache') == []


@requires_redis
@slow
def test_bin_sync_cache(
    env,
    resizetarget_opts,
    image1_name,
    image1_data,
    image1_key,
    redis_cache
):
    resize_target = flask_resize.ResizeTarget(**resizetarget_opts)

    resize_target.image_store.save(image1_name, image1_data)
    resize_target.generate()

    redis_cache.clear()

    assert run(env, 'flask-resize', 'list', 'cache') == []

    run(env, 'flask-resize', 'sync', 'cache')

    assert run(env, 'flask-resize', 'list', 'images') == [image1_key]
