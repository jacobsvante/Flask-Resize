from nose.tools import assert_equal
from flask_resize import safe_placeholder_filename, hexvalue


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
