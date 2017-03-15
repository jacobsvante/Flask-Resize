Usage
=====

Usage in Jinja templates
------------------------

After having :doc:`installed <installation>` and :doc:`configured <configuration>` Flask-Resize in your app the ``resize`` filter should be available in your jinja templates.

Generate an image from the supplied image URL that will fit
within an area of 600px width and 400px height::

    {{ original_image_url|resize('600x400') }}

Resize and crop so that the image will fill the entire area::

    {{ original_image_url|resize('300x300', fill=1) }}

Convert to JPG::

    {{ original_image_url|resize('300x300', format='jpg') }}

List of arguments
-----------------

dimensions
~~~~~~~~~~

Required

Can be either a string or a two item list. The format when using a
string is any of ``<width>x<height>``, ``<width>`` or ``x<height>``. If
width or height is left out they will be determined from the ratio of
the original image. If both width and height are supplied then the
output image will be within those boundries.

placeholder
~~~~~~~~~~~

Default: False

A placeholder image will be returned if the image couldn't be generated.
The placeholder will contain text specifying dimensions, and reason for
image not being generated (either ``empty image path`` or
``<filepath> does not exist``)

format
~~~~~~

Default: Keep original format

If you want to change the format. A white background color is applied when a transparent image is converted to JPEG, or the color specified with ``bgcolor``. Available formats are PNG and JPEG at the moment. Defaults to using the same format as the original.

bgcolor
~~~~~~~

Default: Don't add a background color

Adds a background color to the image. Can be in any of the following
formats:

-  ``#333``
-  ``#333333``
-  ``333``
-  ``333333``
-  ``(51, 51, 51)``

quality
~~~~~~~

Default: ``80``

Only matters if output format is jpeg. Quality of the output image.
0-100.

upscale
~~~~~~~

Default: ``True``

Disable if you don't want the original image to be upscaled if the
dimensions are smaller than those of ``dimensions``.

fill
~~~~

Default: ``False``

The default is to keep the ratio of the original image. With ``fill`` it
will crop the image after resizing so that it will have exactly width
and height as specified.

progressive
~~~~~~~~~~~

Default: True

Whether to use progressive or not. Only matters if the output format is
jpeg. `Article about progressive
JPEGs <http://www.yuiblog.com/blog/2008/12/05/imageopt-4/>`__.
