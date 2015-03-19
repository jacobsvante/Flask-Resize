from nose.tools import assert_equal
from flask_resize import safe_placeholder_filename


def test_safe_filename():
    assert_equal(safe_placeholder_filename('/var/run/myapp.pid'),
                 '-var-run-myapp-pid.png')
