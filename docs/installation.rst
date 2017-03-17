Installation
============

Production version
------------------

To install:

.. code:: sh

    # File-based storage only
    pip install flask-resize

    # With S3 storage support
    pip install flask-resize[s3]

    # With Redis caching
    pip install flask-resize[redis]

    # With SVG source file support (only available with py3.4+)
    pip install flask-resize[svg]

    # With all features above
    pip install flask-resize[full]

Development version
-------------------

.. code:: sh

    pip install -e git+https://github.com/jmagnusson/flask-resize@master#egg=Flask-Resize

Compatibility
-------------

Tested with Python 2.7/3.3+ and with latest version of Flask. Will probably not work on Windows as there are some differences in how paths are handled.

Running the tests
-----------------

.. code:: sh

    git clone https://github.com/jmagnusson/Flask-Resize.git
    cd Flask-Resize
    pip install tox
    tox

Generating the docs
-------------------

.. code:: sh

    git clone https://github.com/jmagnusson/Flask-Resize.git
    cd Flask-Resize
    pip install -r requirements_docs.txt
    python manage.py docs clean build serve

Now you should be able to view the docs @ `localhost:8000 <http://localhost:8000>`_.

Contributing
------------

Fork the code `on the Github project page <https://github.com/jmagnusson/flask-resize>`_ then:

.. code:: sh

    git clone git@github.com:YOUR_USERNAME/Flask-Resize.git
    cd Flask-Resize
    pip install '.[test,svg,redis,s3]' -r requirements_docs.txt
    git checkout -b my-fix
    # Create your fix and add any tests if deemed necessary.
    # Run the test suite to make sure everything works smooth.
    py.test
    git commit -am 'My fix!'
    git push

Now you should see a box on the `project page <https://github.com/jmagnusson/flask-resize>`_ with which you can create a pull request.
