Changelog
=========

1.0.3 (2017-03-17)
------------------

- **Improvement** Add image to cache when the path is found while checking for its existence, even though it wasn't in the local cache since before. This way a path can be cached even though the generation was done on another computer, or after the local cache has been cleared.

1.0.2 (2017-03-17)
------------------

- **Breaking** Removed option `RESIZE_USE_S3` and replaced it with `RESIZE_STORAGE_BACKEND`, more explicit and simple.
- **Improvement** Automatically load `RESIZE_S3_ACCESS_KEY`, `RESIZE_S3_SECRET_KEY` and `RESIZE_S3_REGION` settings using `botocore.session`, in case they are not explicitly specified.

1.0.1 (2017-03-17)
------------------

- **Improvement** Added the option `RESIZE_S3_REGION`. Can be set if the S3 region has to be specified manually for some reason.

1.0.0 (2017-03-17)
------------------

Flask-Resize 1.0  🎊  🍻  🎈  🎉

The big changes are:

- **Feature** Support Amazon S3 as a storage backend
- **Feature** Support Redis caching. The usefulness of this is threefold:
    1. When using S3 as a storage backend to save on HTTP requests
    2. No need to check if file exists on file storage backends - perhaps noticable on servers with slow disk IO
    3. Much lower chance of multiple threads/processes trying to generate the
       same image at the same time.
- **Breaking** Please note that this release forces all generated images to be recreated because of a change in the creation of the "unique key" which is used to determine if the image has already been generated.
- **Breaking** Drop RESIZE_HASH_FILENAME as an option - always hash the cache object's filename. Less moving parts in the machinery.
- **Breaking** Rename RESIZE_CACHE_DIR to RESIZE_TARGET_DIRECTORY to better reflect what the setting does, now that we have Redis caching.
- **Breaking** Use SHA1 as default filename hashing method for less likelyhood of collision

0.8.0 (2016-10-01)
------------------

- **Improvement** Release as a universal python wheel

0.8.0 (2016-09-07)
------------------

- **Feature** Support SVG as input format by utilizing [CairoSVG](http://cairosvg.org/).

0.7.0 (2016-09-01)
------------------

- **Improvement** Keep ICC profile from source image
- **Minor fix** Clarify that Python 3.5 is supported

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
