# Flask-Resize

[![Travis CI build status (Linux)](https://travis-ci.org/jmagnusson/Flask-Resize.svg?branch=master)](https://travis-ci.org/jmagnusson/Flask-Resize)
[![PyPI version](https://img.shields.io/pypi/v/Flask-Resize.svg)](https://pypi.python.org/pypi/Flask-Resize/)
[![Downloads from PyPI per month](https://img.shields.io/pypi/dm/Flask-Resize.svg)](https://pypi.python.org/pypi/Flask-Resize/)
[![License](https://img.shields.io/pypi/l/Flask-Resize.svg)](https://pypi.python.org/pypi/Flask-Resize/)
[![Available as wheel](https://img.shields.io/pypi/wheel/Flask-Resize.svg)](https://pypi.python.org/pypi/Flask-Resize/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/Flask-Resize.svg)](https://pypi.python.org/pypi/Flask-Resize/)
[![PyPI status (alpha/beta/stable)](https://img.shields.io/pypi/status/Flask-Resize.svg)](https://pypi.python.org/pypi/Flask-Resize/)
[![Coverage Status](https://coveralls.io/repos/jmagnusson/Flask-Resize/badge.svg?branch=master)](https://coveralls.io/r/jmagnusson/Flask-Resize?branch=master)
[![Code Health](https://landscape.io/github/jmagnusson/Flask-Resize/master/landscape.svg?style=flat)](https://landscape.io/github/jmagnusson/Flask-Resize/master)


## About

Flask extension for resizing images in your code and templates. Can convert from JPEG|PNG|SVG to JPEG|PNG, resize to fit and crop. File-based and S3-based storage options are available.

Created by [Jacob Magnusson](https://twitter.com/jacobsvante_).

## Installation

    pip install flask-resize

    # With S3
    pip install flask-resize[s3]

    # With Redis caching
    pip install flask-resize[redis]

    # With SVG source file support
    pip install flask-resize[svg]

    # With all features above
    pip install flask-resize[full]

## Documentation

Found @ [flask-resize.readthedocs.io](https://flask-resize.readthedocs.io/).
