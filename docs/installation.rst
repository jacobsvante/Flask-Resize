Installation
============

Production version
------------------

.. code:: sh

    pip install Flask-Resize

Development version
-------------------

.. code:: sh

    pip install -e git+https://github.com/jmagnusson/flask-resize@master#egg=Flask-Resize $(which python)

Compatibility
-------------

Known to work with Python 2.7 / 3.4 and Flask 0.10. Will probably not work on Windows as there are some differences in how paths are handled.

Running the tests
-----------------

.. code:: sh

    git clone https://github.com/jmagnusson/Flask-Resize.git
    cd Flask-Resize
    pip install -r requirements.txt -r requirements_test.txt

Generating the docs
-------------------

.. code:: sh

    git clone https://github.com/jmagnusson/Flask-Resize.git
    cd Flask-Resize
    pip install -r requirements.txt -r requirements_docs.txt
    python manage.py docs clean build serve

Now you should be able to view the docs @ `localhost:8000 <http://localhost:8000>`_.

Contributing
------------

Fork the code `on the Github project page <https://github.com/jmagnusson/flask-resize>`_ then:

.. code:: sh

    git clone git@github.com:YOUR_USERNAME/Flask-Resize.git
    cd Flask-Resize
    pip install -r requirements.txt -r requirements_test.txt -r requirements_docs.txt
    git checkout -b my-fix
    # Create your fix and add any tests if deemed necessary.
    # Run the test suite to make sure everything works smooth.
    py.test
    git commit -am 'My fix!'
    git push

Now you should see a box on the `project page <https://github.com/jmagnusson/flask-resize>`_ with which you can create a pull request.
