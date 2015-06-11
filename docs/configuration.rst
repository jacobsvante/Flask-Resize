Configuration
=============

Required
--------

You need to set at least two configuration options for your Flask app.

.. code:: python

    # Where your media resides
    RESIZE_ROOT = '/path/to/your/media/root/'

    # The URL where your media is served at. For the best performance you
    # should serve your media with a proper web server, under a subdomain
    # and with cookies turned off.
    RESIZE_URL = 'http://media.yoursite.com/'

Optional
--------

There are also some optional settings (defaults listed below):

.. code:: python

    # Where the resized images should be saved. Relative to RESIZE_ROOT.
    RESIZE_CACHE_DIR = 'cache'

    # Set to False if you want Flask-Resize to create sub-directories for
    # each resize setting instead of using a hash.
    RESIZE_HASH_FILENAME = True

    # Change if you want to use something other than md5 for your hashes.
    # Supports all methods that hashlib supports.
    RESIZE_HASH_METHOD = 'md5'

To configure Flask-Resize for your app:

.. code:: python

    from flask.ext.resize import Resize
    app = Flask(__name__)
    app.config.from_pyfile('/path/to/myconfig.py')
    resize = Resize(app)

Or if using a factory function when creating the app:

.. code:: python

    from flask.ext.resize import Resize
    resize = Resize()
    ...
    app = create_app('/path/to/myconfig.py')
    resize.init_app(app)
