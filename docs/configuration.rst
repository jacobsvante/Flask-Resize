Configuration
=============

Setting up your flask app to use Flask-Resize
---------------------------------------------

Using direct initialization::

    import flask
    import flask_resize

    app = flask.Flask(__name__)
    app.config['RESIZE_URL'] = 'https://mysite.com/'
    app.config['RESIZE_ROOT'] = '/home/user/myapp/images'

    flask_resize.Resize(app)

Using the app factory pattern::

    import flask
    import flask_resize

    resize = flask_resize.Resize()

    def create_app(**config_values):
        app = flask.Flask()
        app.config.update(**config_values)
        resize.init_app(app)
        return app

    # And later on...
    app = create_app(RESIZE_URL='https://mysite.com/',
                     RESIZE_ROOT='/home/user/myapp/images')


Available settings
------------------

Required
~~~~~~~~

You need to set at least two configuration options for your Flask app.

.. code:: python

    # Where your media resides
    RESIZE_ROOT = '/path/to/your/media/root/'

    # The URL where your media is served at. For the best performance you
    # should serve your media with a proper web server, under a subdomain
    # and with cookies turned off.
    RESIZE_URL = 'http://media.yoursite.com/'

Optional
~~~~~~~~

There are also some optional settings (defaults listed below):

.. code:: python

    # Where the resized images should be saved. Relative to RESIZE_ROOT.
    RESIZE_CACHE_DIR = 'cache'

.. code:: python

    # Set to False if you want Flask-Resize to create sub-directories for
    # each resize setting instead of using a hash.
    RESIZE_HASH_FILENAME = True

.. code:: python

    # Change if you want to use something other than md5 for your hashes.
    # Supports all methods that hashlib supports.
    RESIZE_HASH_METHOD = 'md5'

.. code:: python
    # Useful when testing. Makes Flask-Resize skip all processing and just
    # return the original image.
    RESIZE_NOOP = False

.. versionadded:: 0.4.0
   ``RESIZE_NOOP`` was added.
