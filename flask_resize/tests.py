import flask
from nose.tools import assert_equal, assert_raises, assert_is_instance
from flask_resize import Resize, resize, safe_placeholder_filename, hexvalue


def _resizeapp(**settings):
    app = flask.Flask(__name__)
    app.config.update(settings)
    Resize(app)
    return app


def test_safe_filename():
    assert_equal(safe_placeholder_filename('/var/run/myapp.pid'),
                 '-var-run-myapp-pid.png')


def test_hexvalue():
    assert_equal(hexvalue((0, 0, 0)), '#000000')
    assert_equal(hexvalue((20, 50, 200)), '#1432c8')
    assert_equal(hexvalue('000'), '#000000')
    assert_equal(hexvalue('f0c'), '#ff00cc')
    assert_equal(hexvalue('1432c8'), '#1432c8')
    assert_equal(hexvalue('#feccde'), '#feccde')


def test_resize_settings():
    assert_raises(RuntimeError, _resizeapp)
    assert_raises(RuntimeError, _resizeapp, RESIZE_URL='http://test.dev')
    assert_raises(RuntimeError, _resizeapp, RESIZE_ROOT='/')

    working_app = _resizeapp(RESIZE_URL='http://test.dev', RESIZE_ROOT='/')
    assert_is_instance(working_app, flask.Flask)

