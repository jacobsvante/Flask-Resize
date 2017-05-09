import pytest

from flask_resize import _compat

slow = pytest.mark.skipif(
    pytest.config.getoption("--skip-slow"),
    reason="--skip-slow passed in, skipping..."
)

requires_redis = pytest.mark.skipif(
    _compat.redis is None,
    reason='Redis is not installed'
)

requires_boto3 = pytest.mark.skipif(
    _compat.boto3 is None,
    reason='`boto3` has to be installed to run this test'
)

requires_cairosvg = pytest.mark.skipif(
    _compat.cairosvg is None,
    reason="CairoSVG 2.0+ is not installed. Only supported in Python 3.4+"
)

requires_no_cairosvg = pytest.mark.skipif(
    _compat.cairosvg is not None,
    reason="Should only test CairoSVG import error when it isn't installed"
)
