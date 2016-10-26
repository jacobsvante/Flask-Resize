#!-*- coding: utf-8 -*-
"""
:author: Stefan Lehmann
:email: stefan.st.lehmann@gmail.com
:created: 2016-10-26

"""
import os
import os.path as op
import shutil
import hashlib

import flask
import flask_resize as fr
import pytest

from .base import create_resizeapp, create_tmp_images


def _hash_file(filepath):
    hash_ = hashlib.md5()
    with open(filepath, 'rb') as f:
        hash_.update(f.read())
    return hash_.hexdigest()


def test_resize_filter_on_changed_image():

    resize_url = 'http://test.dev/'
    resize_root, images, filenames = create_tmp_images()
    fn0, fn1 = filenames
    app = create_resizeapp(RESIZE_URL=resize_url, RESIZE_ROOT=resize_root,
                           DEBUG=True, RESIZE_TRACKING=True)

    template = (
        '<img src="{{ url_for("static", filename=fn)|resize("100x") }}">'
        '<img src="{{ url_for("static", filename=fn)|resize("200x") }}">'
    )

    # create path for resized image 100x
    fn0_100_path = op.join(resize_root, fr._construct_relative_cache_path(
        fn0, 'png', 100, 'auto', 'no-fill', 'upscale')
    )
    # create path for resized image 200x
    fn0_200_path = op.join(resize_root, fr._construct_relative_cache_path(
        fn0, 'png', 200, 'auto', 'no-fill', 'upscale')
    )

    with app.test_request_context():
        flask.render_template_string(template, fn=fn0)

    # creat hashes for old files
    old_image_hashes = (_hash_file(fn0_100_path), _hash_file(fn0_200_path))

    # remove original image
    os.remove(op.join(resize_root, fn0))

    # replace by new image
    shutil.copy(op.join(resize_root, fn1), op.join(resize_root, fn0))

    # rerender
    with app.test_request_context():
        flask.render_template_string(template, fn=fn0)

    # creat hashes for new file
    new_image_hashes = (_hash_file(fn0_100_path), _hash_file(fn0_200_path))

    for i in range(len(new_image_hashes)):
        assert(old_image_hashes[i] != new_image_hashes[i])
