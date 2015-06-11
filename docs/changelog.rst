Changelog
=========

0.5.0 (2015-06-10)
------------------

- [improvement] Proper documentation, hosted on ``RTD``
- [improvement] Properly documented all functions and classes
- [improvement] Continuous integration with ``Travis CI``
- [improvement] Code coverage with ``coveralls``
- [improvement] More tests
- [change] Dropped ``nose`` in favor of ``py.test``
- [change] Removed unused method ``Resize.teardown``

0.4.0 (2015-04-28)
------------------

-  [feature] Adds the setting ``RESIZE_NOOP`` which will just return the
   passed in image path, as is. This was added to ease the pain of unit
   testing when Flask-Resize is a part of the project.
-  [change] Added more tests

0.3.0 (2015-04-23)
------------------

-  [feature] Adds the ``bgcolor`` option for specifying a background
   color to apply to the image.

0.2.5 (2015-03-20)
------------------

-  [bugfix] Because of a logic error no exception was raised when file
   to resize didn't exist

0.2.4 (2015-03-19)
------------------

-  [bugfix] Fix for pip parse\_requirements syntax change (fixes #6)

0.2.3 (2015-01-30)
------------------

-  [feature] Python 3.4 support (might work in other Pythons as well)

0.2.2 (2014-02-01)
------------------

-  [bugfix] Placeholders were being regenerated on each page load.

0.2.1 (2013-12-09)
------------------

-  [bugfix] Same placeholder reason text was used for all resizes with
   identical dimensions

0.2.0 (2013-12-04)
------------------

-  [feature] Support for generating image placeholders

0.1.1 (2013-11-09)
------------------

-  [bugfix] Format argument wasn't respected
-  [change] Bumped default JPEG quality to 80

0.1.0 (2013-11-09)
------------------

-  Initial version
