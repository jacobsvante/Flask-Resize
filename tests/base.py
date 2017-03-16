import flask
from flask_resize import Resize


def create_resizeapp(RESIZE_ROOT=None, **settings):
    app = flask.Flask(
        __name__,
        static_folder=RESIZE_ROOT,
        static_url_path='/',
    )
    app.config.update(settings, RESIZE_ROOT=RESIZE_ROOT, TESTING=True)
    Resize(app)
    return app
