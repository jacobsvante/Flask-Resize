import os

import flask
import pytest

from .base import create_resizeapp


def test_resize_settings():
    with pytest.raises(RuntimeError):
        create_resizeapp()
    with pytest.raises(RuntimeError):
        create_resizeapp(RESIZE_URL='http://test.dev')
    with pytest.raises(RuntimeError):
        create_resizeapp(RESIZE_ROOT=os.sep)

    working_app = create_resizeapp(RESIZE_URL='http://test.dev',
                                   RESIZE_ROOT=os.sep)
    assert isinstance(working_app, flask.Flask)


def test_resize_noop():
    app = create_resizeapp(RESIZE_NOOP=True)
    with app.test_request_context():
        generated_image_path = app.resize('xyz.png', 'WxH')
    assert generated_image_path == 'xyz.png'
