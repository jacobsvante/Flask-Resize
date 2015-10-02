import os.path as op
import flask
from .base import create_resizeapp, create_tmp_images
import flask_resize as fr


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
