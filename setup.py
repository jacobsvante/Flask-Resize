#!/usr/bin/env python
"""
Flask-Resize
------------

Flask extension for automating the resizing of images in your code and
templates. Can convert from JPEG|PNG|SVG to JPEG|PNG, resize to fit and crop.
File-based and S3-based storage options are available.

See https://flask-resize.readthedocs.io/ for documentation.

"""
from __future__ import print_function

import sys

from setuptools import setup, find_packages


appname = 'Flask-Resize'
pkgname = appname.lower().replace('-', '_')
metadata_relpath = '{}/metadata.py'.format(pkgname)

# Get package metadata. We use exec here instead of importing the
# package directly, so we can avoid any potential import errors.
with open(metadata_relpath) as fh:
    metadata = {}
    exec(fh.read(), globals(), metadata)

setup(
    name=appname,
    version=metadata['__version__'],
    description='Flask extension for resizing images in code and templates',
    long_description=__doc__,
    packages=find_packages(),
    package_dir={pkgname: pkgname},
    package_data={
        pkgname: [
            'fonts/*.ttf',
        ],
    },
    install_requires=[
        'argh',
        'Flask',
        'pilkit',
        'Pillow',
    ],
    extras_require={
        'svg': ['cairosvg'],
        'redis': ['redis'],
        's3': ['boto3'],
        'full': (
            ['redis', 'boto3'] +
            (['cairosvg'] if sys.version_info >= (3, 4) else [])
        ),
        'test': [
            'click>=6.7',
            'coverage>=4.2',
            'pytest>=3.0.7',
        ],
        'test_s3': ['moto>=0.4.31'],
    },
    entry_points={
        'console_scripts': {
            'flask-resize = flask_resize.bin:parser.dispatch',
        },
    },
    author='Jacob Magnusson',
    author_email='m@jacobian.se',
    url='https://github.com/jmagnusson/Flask-Resize',
    license='BSD',
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
