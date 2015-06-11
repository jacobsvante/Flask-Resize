import flask
import pytest
from flask_resize import Resize, resize


def resizeapp(**settings):
    app = flask.Flask(__name__)
    app.config.update(settings)
    Resize(app)
    return app


def test_resize_settings():
    with pytest.raises(RuntimeError):
        resizeapp()
    with pytest.raises(RuntimeError):
        resizeapp(RESIZE_URL='http://test.dev')
    with pytest.raises(RuntimeError):
        resizeapp(RESIZE_ROOT='/')

    working_app = resizeapp(RESIZE_URL='http://test.dev', RESIZE_ROOT='/')
    assert isinstance(working_app, flask.Flask)


def test_resize_noop():
    app = resizeapp(RESIZE_NOOP=True)
    with app.test_request_context():
        generated_image_path = resize('xyz.png', 'WxH')
    assert generated_image_path == 'xyz.png'
