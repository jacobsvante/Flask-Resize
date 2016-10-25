import os
import os.path as op
import tempfile
import shutil
import hashlib

import flask
import flask_resize as fr
import pytest

from .base import create_resizeapp, create_tmp_images


def test_resize_with_hashing():
    resize_url = 'http://test.dev/'
    resize_root, images, filenames = create_tmp_images()
    fn0, fn1 = filenames
    app = create_resizeapp(RESIZE_URL=resize_url, RESIZE_ROOT=resize_root)

    with app.test_request_context():
        image_url = flask.url_for("static", filename=fn0)
        expected_path = fr._construct_relative_cache_path(fn0, 'jpeg', 60, 200, 300, '', 'no-fill', 'upscale', '')
        expected_url = op.join(resize_url, expected_path)
        generated_url = fr.resize(image_url, '200x300', format='jpg', quality=60)
        assert expected_url == generated_url


def test_resize_no_hashing():
    resize_url = 'http://test.dev/'
    resize_root, images, filenames = create_tmp_images()
    fn0, fn1 = filenames
    app = create_resizeapp(RESIZE_URL=resize_url, RESIZE_ROOT=resize_root,
                           RESIZE_HASH_FILENAME=False)

    with app.test_request_context():
        image_url = flask.url_for("static", filename=fn0)
        expected_path = fr._construct_relative_cache_path(fn0, 'jpeg', 60, 200, 300, '', 'no-fill', 'upscale', '', hash_filename=False)
        expected_url = op.join(resize_url, expected_path)
        generated_url = fr.resize(image_url, '200x300', format='jpg', quality=60)
        assert expected_url == generated_url


def test_resize_filter():
    resize_url = 'http://test.dev/'
    resize_root, images, filenames = create_tmp_images()
    fn0, fn1 = filenames
    app = create_resizeapp(RESIZE_URL=resize_url, RESIZE_ROOT=resize_root,
                           DEBUG=True)
    template = '<img src="{{ url_for("static", filename=fn)|resize("100x") }}">'

    expected_path = fr._construct_relative_cache_path(fn0, 'png', 100, 'auto', 'no-fill', 'upscale')
    expected_url = op.join(resize_url, expected_path)

    @app.route('/')
    def start():
        return flask.render_template_string(template, fn=fn0)

    with app.test_request_context():
        rendered = flask.render_template_string(template, fn=fn0)
        assert 'http://test.dev/cache' in rendered

    with app.test_client() as c:
        resp = c.get('/')
        assert expected_url in resp.get_data(True)


def test_fill_dimensions():
    resize_root, images, filenames = create_tmp_images()
    white_img_fn, black_img_fn = filenames
    generated_img = fr.generate_image(
        op.join(resize_root, black_img_fn),
        op.join(resize_root, 'resized_black1.png'),
        width=600, height=700, format=fr.PNG, fill=True
    )
    assert generated_img.width == 600
    assert generated_img.height == 700
    assert generated_img.getpixel((0, 0))[3] == 0  # Transparent

    generated_img = fr.generate_image(
        op.join(resize_root, black_img_fn),
        op.join(resize_root, 'resized_black2.jpg'),
        width=600, height=700, format=fr.JPEG, fill=True,
    )
    assert generated_img.width == 600
    assert generated_img.height == 700
    assert generated_img.getpixel((0, 0)) == (255, 255, 255, 255)

    generated_img = fr.generate_image(
        op.join(resize_root, black_img_fn),
        op.join(resize_root, 'resized_black3.jpg'),
        width=600, height=700, format=fr.JPEG, fill=True,
        bgcolor=(100, 100, 100),
    )
    assert generated_img.width == 600
    assert generated_img.height == 700
    assert generated_img.getpixel((0, 0)) == (100, 100, 100, 255)


SVG_DATA = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="100px" height="100px" viewBox="0 0 100 100" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <defs></defs>
    <rect id="Rectangle" fill="#000000" x="0" y="0" width="100" height="100"></rect>
</svg>"""


@pytest.mark.skipif(
    fr.cairosvg is None,
    reason="CairoSVG 2.0 only supported in 3.4+"
)
def test_svg_resize():
    resize_root = tempfile.mkdtemp()
    svg_path = op.join(resize_root, 'test.svg')
    with open(svg_path, 'w') as fp:
        fp.write(SVG_DATA)

    generated_img = fr.generate_image(
        svg_path,
        op.join(resize_root, 'out.png'),
        format='png',
        width=50,
        height=50
    )
    assert generated_img.width == 50
    assert generated_img.height == 50

    expected = (0, 0, 0, 255)
    assert generated_img.getpixel((0, 0)) == expected
    assert generated_img.getpixel((49, 49)) == expected


@pytest.mark.skipif(
    fr.cairosvg is not None,
    reason="Should only test CairoSVG import error when it isn't installed"
)
def test_svg_resize_cairosvgimporterror():
    resize_root = tempfile.mkdtemp()
    svg_path = op.join(resize_root, 'test.svg')
    with open(svg_path, 'w') as fp:
        fp.write('123')

    with pytest.raises(fr.exc.CairoSVGImportError):
        fr.generate_image(
            svg_path,
            op.join(resize_root, 'out.png'),
            format='png',
            width=50,
            height=50
        )


def test_resize_filter_on_changed_image():
    resize_url = 'http://test.dev/'
    resize_root, images, filenames = create_tmp_images()
    fn0, fn1 = filenames
    app = create_resizeapp(RESIZE_URL=resize_url, RESIZE_ROOT=resize_root,
                           DEBUG=True)
    template = '<img src="{{ url_for("static", filename=fn)|resize("100x") }}">'

    fn0_path = op.join(resize_root, fr._construct_relative_cache_path(
        fn0, 'png', 100, 'auto', 'no-fill', 'upscale')
    )

    with app.test_request_context():
        flask.render_template_string(template, fn=fn0)

    # creat hash for old file
    old_hash = hashlib.md5()
    with open(fn0_path, 'rb') as f:
        old_hash.update(f.read())

    # remove old file
    os.remove(op.join(resize_root, fn0))

    # replace by new file
    shutil.copy(op.join(resize_root, fn1), op.join(resize_root, fn0))

    # rerender
    with app.test_request_context():
        flask.render_template_string(template, fn=fn0)

    # creat hash for new file
    new_hash = hashlib.md5()
    with open(fn0_path, 'rb') as f:
        new_hash.update(f.read())

    assert(old_hash.hexdigest() != new_hash.hexdigest())


if __name__ == '__main__':
    test_resize_filter_on_changed_image()