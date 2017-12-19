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

    resize = flask_resize.Resize(app)

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
    app = create_app(
        RESIZE_URL='https://mysite.com/',
        RESIZE_ROOT='/home/user/myapp/images'
    )

.. _standalone-usage:

Setting up for standalone usage
-------------------------------

One doesn't actually need to involve Flask at all to utilize the resizing (perhaps one day we'll break out the actual resizing into its own package). E.g::

    import flask_resize

    config = flask_resize.configuration.Config(
        url='https://mysite.com/',
        root='/home/user/myapp/images',
    )

    resize = flask_resize.make_resizer(config)

.. versionadded:: 2.0.0
   Standalone mode was introduced


Available settings
------------------

Required for ``file`` storage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to set at least two configuration options when using the default ``file`` storage:

.. code:: python

    # Where your media resides
    RESIZE_ROOT = '/path/to/your/media/root/'

    # The URL where your media is served at. For the best performance you
    # should serve your media with a proper web server, under a subdomain
    # and with cookies turned off.
    RESIZE_URL = 'http://media.yoursite.com/'


Required for ``s3`` storage
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For Amazon S3 storage you only need to do the following if you've already
configured Amazon Web Services with ``aws configure`` (or similar). Default
section configuration can then be extracted using the included ``botocore``
package.

.. code:: python

    RESIZE_STORAGE_BACKEND = 's3'
    RESIZE_S3_BUCKET = 'mybucket'

If you haven't done so then you need to manually specify the following options in addition to above:

.. code:: python

    RESIZE_S3_ACCESS_KEY = 'dq8rJLaMtkHEze4example3C1V'
    RESIZE_S3_SECRET_KEY = 'MC9T4tRqXQexample3d1l7C9sG3M9qes0VEHiNJTG24q4a5'
    RESIZE_S3_REGION = 'eu-central-1'

.. versionadded:: 1.0.0
   ``RESIZE_S3_ACCESS_KEY``, ``RESIZE_S3_SECRET_KEY`` and ``RESIZE_S3_BUCKET`` were added.

.. versionadded:: 1.0.1
   ``RESIZE_S3_REGION`` was added.

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

    # Which backend to store files in. Defaults to the `file` backend.
    # Can be either `file` or `s3`.
    RESIZE_STORAGE_BACKEND = 'file'

    # Which cache store to use. Currently only redis is supported (`pip install
    # flask-resize[redis]`), and will be configured automatically if the
    # package is installed and `RESIZE_CACHE_STORE` hasn't been set
    # explicitly. Otherwise a no-op cache is used.
    RESIZE_CACHE_STORE = 'noop' if redis is None else 'redis'

    # Which host to use for redis if it is enabled with `RESIZE_CACHE_STORE`
    # This can also be a pre-configured `redis.StrictRedis` instance, in which
    # case the redis options below are ignored by Flask-Resize.
    RESIZE_REDIS_HOST = 'localhost'

    # Which port to use for redis if it is enabled with `RESIZE_CACHE_STORE`
    RESIZE_REDIS_PORT = 6379

    # Which db to use for redis if it is enabled with `RESIZE_CACHE_STORE`
    RESIZE_REDIS_DB = 0

    # Which password to use for redis if it is enabled with `RESIZE_CACHE_STORE`. Defaults to not using a password.
    RESIZE_REDIS_PASSWORD = None

    # Which key to use for redis if it is enabled with `RESIZE_CACHE_STORE`
    RESIZE_REDIS_KEY = 0

    # If True then GenerateInProgress exceptions aren't swallowed. Default is
    # to only raise these exceptions when Flask is configured in debug mode.
    RESIZE_RAISE_ON_GENERATE_IN_PROGRESS = app.debug

.. versionadded:: 0.4.0
   ``RESIZE_NOOP`` was added.

.. versionadded:: 1.0.0
   ``RESIZE_CACHE_STORE``, ``RESIZE_REDIS_HOST``, ``RESIZE_REDIS_PORT``, ``RESIZE_REDIS_DB`` and ``RESIZE_REDIS_KEY`` were added.

.. versionadded:: 1.0.2
   ``RESIZE_STORAGE_BACKEND`` was added.

.. versionadded:: 1.0.4
   ``RESIZE_RAISE_ON_GENERATE_IN_PROGRESS`` was added.


.. versionadded:: 2.0.3
   ``RESIZE_REDIS_PASSWORD`` was added.
