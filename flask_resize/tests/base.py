import os.path as op
import tempfile
import flask
from PIL import Image
from flask_resize import Resize


def create_tmp_images():
    resize_root = tempfile.mkdtemp()

    images = (
        Image.new("RGB", (512, 512), "white"),
        Image.new("RGB", (512, 512), "black"),
    )
    image_filenames = tuple('image%s.png' % i for i, _ in enumerate(images))

    for img_filename, img in zip(image_filenames, images):
        img.save(op.join(resize_root, img_filename))

    return resize_root, images, image_filenames


def create_resizeapp(RESIZE_ROOT=None, **settings):
    app = flask.Flask(__name__,
                      static_folder=RESIZE_ROOT,
                      static_url_path='/')
    app.config.update(settings, RESIZE_ROOT=RESIZE_ROOT, TESTING=True)
    Resize(app)
    return app
