import io
import re

import flask
import pytest
from PIL import Image
from flask_resize import _compat, cache, exc, resizing

from .base import create_resizeapp


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


def test_resizetarget_generate(filetarget, image1_data):
    assert filetarget.name_hashing_method == 'sha1'
    expected_unique_key = (
        'resized-images/d346d9b67bf93454629a5125f273143818bbd6d2.jpg'
    )

    with pytest.raises(exc.CacheMiss):
        filetarget.get_cached_path()

    with pytest.raises(exc.ImageNotFoundError):
        assert filetarget.get_path()

    # Save original file
    filetarget.image_store.save('image.png', image1_data)

    # Generate thumb
    filetarget.generate()

    assert filetarget.get_path() == expected_unique_key


# @pytest.mark.usefixtures('inspect_filetarget_directory')
def test_resizetarget_generate_placeholder(filetarget, image1_data):
    filetarget.use_placeholder = True
    filetarget.generate()

    assert re.match(r'^resized-images/.+\.jpg$', filetarget.get_path())


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

    # expected_path = fr._construct_relative_cache_path(fn0, 'png', 100, 'auto', 'no-fill', 'upscale')
    # expected_url = op.join(resize_url, expected_path)

    @app.route('/')
    def start():
        return flask.render_template_string(template, fn='file1.png')

    with app.test_client() as c:
        resp = c.get('/')
        assert file1_expected_url in resp.get_data(True)

    with app.test_request_context():
        rendered = flask.render_template_string(template, fn='file2.png')
        assert file2_expected_url in rendered


def test_fill_dimensions(tmpdir, image1_data, default_filetarget_options):
    file1 = tmpdir.join('file1.png')
    file1.write_binary(image1_data)

    options = default_filetarget_options.copy()
    options.update(
        format='png',
        source_image_relative_url='file1.png',
        dimensions='300x400',
        fill=True,
    )
    resize_target = resizing.ResizeTarget(**options)
    img_data = resize_target.generate()
    generated_img = Image.open(io.BytesIO(img_data))
    assert generated_img.width == 300
    assert generated_img.height == 400
    assert generated_img.getpixel((0, 0))[3] == 0  # Transparent

    options.update(dimensions='700x600')
    resize_target = resizing.ResizeTarget(**options)
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


@pytest.mark.skipif(
    _compat.cairosvg is None,
    reason="CairoSVG 2.0 only supported in 3.4+"
)
def test_svg_resize(tmpdir, default_filetarget_options):
    svg_path = tmpdir.join('test.svg')
    svg_path.write(SVG_DATA)

    options = default_filetarget_options.copy()
    options.update(
        format='png',
        source_image_relative_url='test.svg',
        dimensions='50x50',
    )
    resize_target = resizing.ResizeTarget(**options)
    img_data = resize_target.generate()
    img = Image.open(io.BytesIO(img_data))

    assert img.width == 50
    assert img.height == 50

    expected = (0, 0, 0, 255)
    assert img.getpixel((0, 0)) == expected
    assert img.getpixel((49, 49)) == expected


@pytest.mark.skipif(
    _compat.cairosvg is not None,
    reason="Should only test CairoSVG import error when it isn't installed"
)
def test_svg_resize_cairosvgimporterror(tmpdir, default_filetarget_options):
    svg_path = tmpdir.join('test.svg')
    svg_path.write('content')

    options = default_filetarget_options.copy()
    options.update(source_image_relative_url='test.svg')
    resize_target = resizing.ResizeTarget(**options)

    with pytest.raises(exc.CairoSVGImportError):
        resize_target.generate()
