Changelog
=========

0.7.0 (2015-12-03)
------------------

-  **Feature** A path to a default image can now be specified to be
   used as the background for any generated placeholders.
-  **Improvement** Placeholder text now correctly wraps to fit within
   the placeholder's width.
-  **Change** Made placeholder generated solid background darker
-  **Change** Moved placeholder text to the bottom of the generated image

0.6.4 (2015-12-02)
------------------

-  **Improvement** Allowed the passing of a single integer
   representing the width.

0.6.3 (2015-10-24)
------------------

-  **Bugfix** Fixed typos in parts of the code, causing Flask-Resize
   to fail under certain circumstances.

0.6.2 (2015-10-24)
------------------

-  **Feature** Adds the ``force_cache`` to force generating/using
   cache images, even if the generated image is the same size as the
   original image.
-  **Improvement** Now returns the original image path by default if the
   to be generated image is the same size as the original and if no
   other processing is needed.

0.6.1 (2015-10-22)
------------------

- **Bugfix** Now generates correct path output on Windows systems

0.6.0 (2015-10-01)
------------------

- **Bugfix** Fill doesn't cut the image any more

0.5.2 (2015-06-12)
------------------

- **Bugfix** Fix Python 2 regression

0.5.1 (2015-06-12)
------------------

- **Improvement** Tests that actually convert images with the :func:`flask_resize.resize` command.
- **Improvement** Validates that ``RESIZE_ROOT`` and ``RESIZE_URL`` are strings.


0.5.0 (2015-06-10)
------------------

- **Improvement** Proper documentation, hosted on ``RTD``
- **Improvement** Properly documented all functions and classes
- **Improvement** Continuous integration with ``Travis CI``
- **Improvement** Code coverage with ``coveralls``
- **Improvement** More tests
- **Change** Dropped ``nose`` in favor of ``py.test``
- **Change** Removed unused method ``Resize.teardown``

0.4.0 (2015-04-28)
------------------

-  **Feature** Adds the setting ``RESIZE_NOOP`` which will just return the
   passed in image path, as is. This was added to ease the pain of unit
   testing when Flask-Resize is a part of the project.
-  **Change** Added more tests

0.3.0 (2015-04-23)
------------------

-  **Feature** Adds the ``bgcolor`` option for specifying a background
   color to apply to the image.

0.2.5 (2015-03-20)
------------------

-  **Bugfix** Because of a logic error no exception was raised when file
   to resize didn't exist

0.2.4 (2015-03-19)
------------------

-  **Bugfix** Fix for pip parse\_requirements syntax change (fixes #6)

0.2.3 (2015-01-30)
------------------

-  **Feature** Python 3.4 support (might work in other Pythons as well)

0.2.2 (2014-02-01)
------------------

-  **Bugfix** Placeholders were being regenerated on each page load.

0.2.1 (2013-12-09)
------------------

-  **Bugfix** Same placeholder reason text was used for all resizes with
   identical dimensions

0.2.0 (2013-12-04)
------------------

-  **Feature** Support for generating image placeholders

0.1.1 (2013-11-09)
------------------

-  **Bugfix** Format argument wasn't respected
-  **Change** Bumped default JPEG quality to 80

0.1.0 (2013-11-09)
------------------

-  Initial version
