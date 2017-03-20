import logging
import os
import subprocess

import pytest
from PIL import Image

import flask_resize


logging.basicConfig(format='%(levelname)s:%(name)s:%(thread)d:%(message)s')
log_level = os.environ.get('RESIZE_LOG_LEVEL', 'error')
flask_resize.logger.setLevel(getattr(logging, log_level.upper()))


@pytest.yield_fixture
def inspect_filetarget_directory(filetarget):
    yield
    subprocess.run(['open', filetarget.image_store.base_path])


@pytest.fixture
def image1():
    return Image.new("RGB", (512, 512), "red")


@pytest.fixture
def image1_data(image1):
    return flask_resize.resizing.image_data(image1, 'PNG')


@pytest.fixture
def image2():
    return Image.new("RGB", (512, 512), "blue")


@pytest.fixture
def image2_data(image2):
    return flask_resize.resizing.image_data(image2, 'PNG')


@pytest.fixture
def filestorage(tmpdir):
    return flask_resize.storage.FileStorage(base_path=str(tmpdir))


@pytest.fixture
def default_filetarget_options(filestorage):
    return dict(
        image_store=filestorage,
        source_image_relative_url='image.png',
        dimensions='100x50',
        format='jpeg',
        quality=80,
        fill=False,
        bgcolor=None,
        upscale=True,
        progressive=True,
        use_placeholder=False,
        cache_store=flask_resize.cache.NoopCache(),
    )


@pytest.fixture
def filetarget(filestorage, default_filetarget_options):
    return flask_resize.resizing.ResizeTarget(**default_filetarget_options)
