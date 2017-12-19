Installation
============

Production version
------------------

Recommended install with all features (Redis cache + S3 storage + SVG if py3.4+):

.. code:: sh

    pip install flask-resize[full]

Other alternatives:

.. code:: sh

    # File-based storage only
    pip install flask-resize

    # With S3 storage support
    pip install flask-resize[s3]

    # With Redis caching
    pip install flask-resize[redis]

    # With SVG source file support (only available with py3.4+)
    pip install flask-resize[svg]

    # Or any combination of above. E.g:
    pip install flask-resize[s3,redis]

Development version
-------------------

.. code:: sh

    pip install -e git+https://github.com/jmagnusson/flask-resize@master#egg=Flask-Resize

.. _compatibility:

Compatibility
-------------

Tested with Python 2.7/3.4/3.5/3.6/pypy and latest version of Flask.

Should work well on most Linux and MacOS versions.

Windows is supported on paper with the full test suite running smoothly, but  the package needs some real world usage on Windows though. Please report any issues you might find to the Github issues page. Any feedback is welcome! 😊

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
    pip install '.[full,test,test_s3]' -r requirements_docs.txt
    git checkout -b my-fix
    # Create your fix and add any tests if deemed necessary.
    # Run the test suite to make sure everything works smooth.
    py.test
    git commit -am 'My fix!'
    git push

Now you should see a box on the `project page <https://github.com/jmagnusson/flask-resize>`_ with which you can create a pull request.
