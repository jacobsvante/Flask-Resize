import io
import re

import flask
import pytest
from PIL import Image

from flask_resize import cache, exc, resizing

from .base import create_resizeapp
from .decorators import requires_cairosvg, requires_no_cairosvg


def test_resizetarget_init(filestorage):
    original_image_relative_url = 'path/to/my/file.png'
    target = resizing.ResizeTarget(
        filestorage,
        original_image_relative_url,
        dimensions='100x50',
        format='jpeg',
        quality=80,
        fill=False,
        bgcolor=None,
        upscale=True,
        progressive=True,
        use_placeholder=False,
        cache_store=cache.NoopCache(),
    )
    assert target.name_hashing_method == 'sha1'
    assert target.target_directory == 'resized-images'

    assert(
        target._get_generate_unique_key_args() ==
        [
            original_image_relative_url, 'JPEG', 80, 100, 50, '', 'no-fill',
            'upscale', ''
        ]
    )

    assert(
        target.unique_key ==
        'resized-images/e1307a6b8f166778588914d5130bd92bcd7f20ca.jpg'
    )


def test_resizetarget_generate(
    resizetarget_opts,
    image1_data,
    image1_name,
    image1_key
):
    resize_target = resizing.ResizeTarget(**resizetarget_opts)
    assert resize_target.name_hashing_method == 'sha1'

    with pytest.raises(exc.CacheMiss):
        resize_target.get_cached_path()

    with pytest.raises(exc.ImageNotFoundError):
        assert resize_target.get_path()

    # Save original file
    resize_target.image_store.save(image1_name, image1_data)

    # Generate thumb
    resize_target.generate()

    assert resize_target.get_path() == image1_key


def test_resizetarget_generate_placeholder(resizetarget_opts, image1_data):
    resize_target = resizing.ResizeTarget(**resizetarget_opts)
    resize_target.use_placeholder = True
    resize_target.generate()

    assert re.match(r'^resized-images/.+\.jpg$', resize_target.get_path())


def test_resize_filter(tmpdir, image1_data, image2_data):
    resize_url = 'http://test.dev/'
    file1 = tmpdir.join('file1.png')
    file1.write_binary(image1_data)

    file2 = tmpdir.join('file2.png')
    file2.write_binary(image2_data)

    file1_expected_url = (
        resize_url +
        'resized-images/ac17b732cabcc4eeb783cd994d0e169665b3bb68.png'
    )

    file2_expected_url = (
        resize_url +
        'resized-images/add9a8c8531825a56f58289087b1f892c5e1348f.png'
    )

    app = create_resizeapp(
        RESIZE_URL=resize_url,
        RESIZE_ROOT=str(tmpdir),
        DEBUG=True
    )
    template = '<img src="{{ fn|resize("100x") }}">'

    @app.route('/')
    def start():
        return flask.render_template_string(template, fn='file1.png')

    with app.test_client() as c:
        resp = c.get('/')
        assert file1_expected_url in resp.get_data(True)

    with app.test_request_context():
        rendered = flask.render_template_string(template, fn='file2.png')
        assert file2_expected_url in rendered


def test_fill_dimensions(tmpdir, image1_data, resizetarget_opts):
    file1 = tmpdir.join('file1.png')
    file1.write_binary(image1_data)

    resizetarget_opts.update(
        format='png',
        source_image_relative_url='file1.png',
        dimensions='300x400',
        fill=True,
    )
    resize_target = resizing.ResizeTarget(**resizetarget_opts)
    img_data = resize_target.generate()
    generated_img = Image.open(io.BytesIO(img_data))
    assert generated_img.width == 300
    assert generated_img.height == 400
    assert generated_img.getpixel((0, 0))[3] == 0  # Transparent

    resizetarget_opts.update(dimensions='700x600')
    resize_target = resizing.ResizeTarget(**resizetarget_opts)
    img_data = resize_target.generate()
    generated_img = Image.open(io.BytesIO(img_data))
    assert generated_img.width == 700
    assert generated_img.height == 600
    assert generated_img.getpixel((0, 0))[3] == 0  # Transparent


SVG_DATA = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="100px" height="100px" viewBox="0 0 100 100" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <defs></defs>
    <rect id="Rectangle" fill="#000000" x="0" y="0" width="100" height="100"></rect>
</svg>"""


@requires_cairosvg
def test_svg_resize(tmpdir, resizetarget_opts):
    svg_path = tmpdir.join('test.svg')
    svg_path.write(SVG_DATA)

    resizetarget_opts.update(
        format='png',
        source_image_relative_url='test.svg',
        dimensions='50x50',
    )
    resize_target = resizing.ResizeTarget(**resizetarget_opts)
    img_data = resize_target.generate()
    img = Image.open(io.BytesIO(img_data))

    assert img.width == 50
    assert img.height == 50

    expected = (0, 0, 0, 255)
    assert img.getpixel((0, 0)) == expected
    assert img.getpixel((49, 49)) == expected


@requires_no_cairosvg
def test_svg_resize_cairosvgimporterror(tmpdir, resizetarget_opts):
    svg_path = tmpdir.join('test.svg')
    svg_path.write('content')

    resizetarget_opts.update(source_image_relative_url='test.svg')
    resize_target = resizing.ResizeTarget(**resizetarget_opts)

    with pytest.raises(exc.CairoSVGImportError):
        resize_target.generate()
