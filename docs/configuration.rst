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

You need to set at least two configuration options when using the default file-based storage:

.. code:: python

    # Where your media resides
    RESIZE_ROOT = '/path/to/your/media/root/'

    # The URL where your media is served at. For the best performance you
    # should serve your media with a proper web server, under a subdomain
    # and with cookies turned off.
    RESIZE_URL = 'http://media.yoursite.com/'

For Amazon S3 storage you only need to do the following if you've already
configured Amazon Web Services with `aws configure` (or similar). Default
section configuration can then be extracted using the `boto3` package.

.. code:: python

    RESIZE_STORAGE_BACKEND = 's3'
    RESIZE_S3_SECRET_KEY = 'mybucket'

If you haven't done so then you need to manually specify the following options:

.. code:: python

    RESIZE_STORAGE_BACKEND = 's3'
    RESIZE_S3_ACCESS_KEY = 'dq8rJLaMtkHEze4example3C1V'
    RESIZE_S3_SECRET_KEY = 'MC9T4tRqXQexample3d1l7C9sG3M9qes0VEHiNJTG24q4a5'
    RESIZE_S3_REGION = 'eu-central-1'
    RESIZE_S3_BUCKET = 'mybucket'

.. versionadded:: 1.0.0
   ``RESIZE_S3_ACCESS_KEY``, ``RESIZE_S3_SECRET_KEY`` and ``RESIZE_S3_BUCKET`` were added.

Optional
~~~~~~~~

There are also some optional settings. They are listed below, with their default values.

.. code:: python

    # Where the resized images should be saved. Relative to `RESIZE_ROOT`
    # if using the file-based storage option.
    RESIZE_TARGET_DIRECTORY = 'resized-images'

    # Set to False if you want Flask-Resize to create sub-directories for
    # each resize setting instead of using a hash.
    RESIZE_HASH_FILENAME = True

    # Change if you want to use something other than sha1 for your hashes.
    # Supports all methods that hashlib supports.
    RESIZE_HASH_METHOD = 'sha1'

    # Useful when testing. Makes Flask-Resize skip all processing and just
    # return the original image URL.
    RESIZE_NOOP = False

    # Which backend to store files in. Defaults to the file backend. Can be either `file` or `s3`.
    RESIZE_STORAGE_BACKEND = 'file'

    # Use redis as a cache if it's installed (`pip install
    # flask-resize[redis]`), otherwise use a no-op cache. Can be set
    # to `None` manually to forcefully turn redis caching off, even
    # if the client is installed.
    RESIZE_CACHE_STORE = 'redis' if redis is not None else None

    # Which host to use for redis if it is enabled with `RESIZE_CACHE_STORE`
    RESIZE_REDIS_HOST = 'localhost'

    # Which port to use for redis if it is enabled with `RESIZE_CACHE_STORE`
    RESIZE_REDIS_PORT = 6379

    # Which db to use for redis if it is enabled with `RESIZE_CACHE_STORE`
    RESIZE_REDIS_DB = 0

    # Which key to use for redis if it is enabled with `RESIZE_CACHE_STORE`
    RESIZE_REDIS_KEY = 0

    # Can be set if the S3 region has to be specified manually for some reason.
    RESIZE_S3_REGION = None

.. versionadded:: 0.4.0
   ``RESIZE_NOOP`` was added.

.. versionadded:: 1.0.0
   ``RESIZE_CACHE_STORE``, ``RESIZE_REDIS_HOST``, ``RESIZE_REDIS_PORT``, ``RESIZE_REDIS_DB`` and ``RESIZE_REDIS_KEY`` were added.

.. versionadded:: 1.0.1
   ``RESIZE_S3_REGION``was added.

.. versionadded:: 1.0.2
   ``RESIZE_STORAGE_BACKEND``was added.
