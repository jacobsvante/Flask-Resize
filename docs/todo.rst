To-do
=====

Use default S3-settings if not explicitly set up
------------------------------------------------

Don't require any S3-settings. boto3 automatically reads from `~/.aws/credentials` and `~/.aws/config` if it exists. Perhaps new setting `RESIZE_BACKEND` to configure also.

Automatic fitting of placeholder text
-------------------------------------

See `issue #7 <https://flask-resize.readthedocs.io/en/latest/changelog.html>`_.

Support for signals
-------------------
Generate images directly instead of when web page is first hit.

Windows
-------

Verify Windows support.
