#!/usr/bin/env python
"""
Flask-Resize
------------

Flask extension for resizing images in templates.

See https://github.com/jmagnusson/Flask-Resize for usage.

"""
from __future__ import print_function
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
    description='Flask extension for resizing images in templates',
    long_description=__doc__,
    packages=find_packages(),
    package_dir={pkgname: pkgname},
    package_data={
        pkgname: [
            'fonts/*.ttf',
        ],
    },
    install_requires=[
        'Pillow',
        'pilkit',
        'Flask',
    ],
    entry_points={
        'console_scripts': {},
    },
    author='Jacob Magnusson',
    author_email='m@jacobian.se',
    url='https://github.com/jmagnusson/Flask-Resize',
    license='BSD',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
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
    ],
)
