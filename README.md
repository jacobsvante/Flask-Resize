# Flask-Resize

[![PyPI version](https://pypip.in/v/Flask-Resize/badge.png)](https://pypi.python.org/pypi/Flask-Resize)
[![PyPI downloads](https://pypip.in/d/Flask-Resize/badge.png)](https://pypi.python.org/pypi/Flask-Resize)


Created by [Jacob Magnusson](https://twitter.com/pyjacob), 2013. Full list of contributors can be found [here](CONTRIBUTORS.md).


## About

Flask extension for easily resizing images in templates. Can convert to/from JPEG/PNG, resize to fit and crop.

## Installation

    pip install Flask-Resize


## Compatibility

Haven't had time to add a test suite yet so I can only confirm that it works with Python 2.7 and Flask 0.10 at the moment. Will probably not work in Windows as there are some differences in how paths are handled.


## Configuration


You need to set at least two configuration options for your Flask app.

```python
# Where your media resides
RESIZE_ROOT = '/path/to/your/media/root/'

# The URL where your media is served at. For the best performance you
# should serve your media with a proper web server, under a subdomain
# and with cookies turned off.
RESIZE_URL = 'http://media.yoursite.com/'
```

There are also some optional settings (defaults listed below):

```python
# Where the resized images should be saved. Relative to RESIZE_ROOT.
RESIZE_CACHE_DIR = 'cache'

# Set to False if you want Flask-Resize to create sub-directories for
# each resize setting instead of using a hash.
RESIZE_HASH_FILENAME = True

# Change if you want to use something other than md5 for your hashes.
# Supports all methods that hashlib supports.
RESIZE_HASH_METHOD = 'md5'
```

To configure Flask-Resize for your app:

```python
from flask.ext.resize import Resize
app = Flask(__name__)
app.config.from_pyfile('/path/to/myconfig.py')
resize = Resize(app)
```

Or if using a factory function when creating the app:

```python
from flask.ext.resize import Resize
resize = Resize()
...
app = create_app('/path/to/myconfig.py')
resize.init_app(app)
```

## Documentation

After having configured Flask-Resize the resize filter should be available in your jinja templates.

Some usage examples:

```python
# Generate an image from the supplied image path that will fit
# within an area of 600px width and 400px height.
<img src="{{ img_path|resize('600x400') }}">

# Resize and crop so that the image will fill the entire area
<img src="{{ img_path|resize('300x300', fill=1)" }}>

# Convert to JPG
<img src="{{ img_path|resize('300x300', format='jpg')" }}>
```

The full list of arguments are:

### dimensions
Required

Can be either a string or a two item list. The format when using a string is any of `<width>x<height>`, `<width>` or `x<height>`. If width or height is left out they will be determined from the ratio of the original image. If both width and height are supplied then the output image will be within those boundries.

### format
Default: Keep original format

If you want to change the format. A white background is applied when a transparent image is converted to JPEG. Available formats are PNG and JPEG at the moment.

### quality
Default: 80

Only matters if output format is jpeg. Quality of the output image. 0-100.


### upscale
Default: `True`

Disable if you don't want the original image to be upscaled if the dimensions are smaller than those of `dimensions`.

### fill
Default: `False`

The default is to keep the ratio of the original image. With `fill` it will crop the image after resizing so that it will have exactly width and height as specified. The anchor-point can be changed with the `anchor` option.

### anchor
Default: `center`

Only matters if `fill` is also set. This specifies which part of the image that should be the anchor, i.e. which part that should be retained. Valid choices are `top-left`, `top`, `top-right`, `bottom-left`, `bottom`, `bottom-right`, `center`, `left` and `right`.

### progressive

Default: True

Whether to use progressive or not. Only matters if the output format is jpeg. [Article about progressive JPEGs](http://www.yuiblog.com/blog/2008/12/05/imageopt-4/).
