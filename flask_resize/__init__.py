import errno
import hashlib
import os
import six
from pilkit.processors import Anchor, ResizeToFit, ResizeToFill
from pilkit.utils import save_image
from flask import current_app
from PIL import Image
from .metadata import __version_info__, __version__ # NOQA


JPEG = 'JPEG'
PNG = 'PNG'

VALID_ANCHOR_VALUES = [a for a in vars(Anchor) if a[0].isupper()]


def parse_dimensions(dimensions):
    error_msg = ("Image dimensions must be a string with <width>x<height>, "
                 "<width>, <width>x, x<height>. Or it can be a two item "
                 "list with width and height.")

    if isinstance(dimensions, six.string_types):
        dimensions = dimensions.split('x')
        if len(dimensions) not in (1, 2):
            raise ValueError(error_msg)
        if not any(dimensions):
            raise ValueError(error_msg)
        if len(dimensions) == 1:
            dimensions.append(None)
        dimensions = [d or None for d in dimensions]

    if not isinstance(dimensions, (list, tuple)):
        raise TypeError(error_msg)

    if not len(dimensions) == 2:
        raise ValueError(error_msg)

    return [(int(d) if d else None) for d in dimensions]


def get_root_relative_path(image_url):
    resize_url = current_app.config['RESIZE_URL']

    if image_url.startswith(resize_url):
        image_url = image_url[len(resize_url):]

    return image_url[1:] if image_url.startswith('/') else image_url


def get_relative_cache_path(filename, ext, *path_parts):
    filename_no_ext, _, _ = filename.rpartition('.')
    filename = u'.'.join((filename_no_ext, ext))
    cache_dir = current_app.config['RESIZE_CACHE_DIR']
    cache_path = u'/'.join(str(p) for p in filter(None, path_parts))

    if current_app.config['RESIZE_HASH_FILENAME']:
        hash = hashlib.new(current_app.config['RESIZE_HASH_METHOD'])
        hash.update(cache_path + filename)
        return u'{0}/{1}.{2}'.format(cache_dir, hash.hexdigest(), ext)
    else:
        return os.path.join(cache_dir, cache_path, filename)


def get_anchor(value):
    anchor_attr = value.upper().replace('-', '_')
    if anchor_attr not in VALID_ANCHOR_VALUES:
        raise ValueError('Not a valid anchor value. Valid ones '
                         'are {0}'.format(VALID_ANCHOR_VALUES))
    return getattr(Anchor, anchor_attr)


def mkdir_p(path):
    """mkdir -p equivalent"""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_format(image_url, format):
    if not format:
        _, _, format = image_url.rpartition('.')
    format = format.upper()
    if format == 'JPG':
        format = JPEG
    if format not in (JPEG, PNG):
        raise ValueError("JPEG and PNG are the only supported formats at "
                         "the moment.")
    return format


def generate_image(inpath, outpath, width=None, height=None, format=JPEG,
                   fill=False, upscale=True, anchor=None, quality=80,
                   progressive=True):
    mkdir_p(outpath.rpartition('/')[0])
    img = Image.open(inpath)
    processor_kwargs = dict(width=width, height=height, upscale=upscale)

    if fill:
        processor_kwargs['anchor'] = anchor

    ResizeMethod = ResizeToFill if fill else ResizeToFit
    processor = ResizeMethod(**processor_kwargs)
    new_img = processor.process(img)

    assert (not os.path.exists(outpath),
            'Path to save to already exists')

    options = {}
    if format == JPEG:
        options.update({'quality': int(quality), 'progressive': progressive})

    with open(outpath, 'w') as outfile:
        save_image(new_img, outfile, format=format, options=options)


def resize(image_url, dimensions, format=None, quality=80, fill=False,
           upscale=True, progressive=True, anchor='center'):
    """Jinja filter for resizing (and converting) images

    Usage::

        # Generate an image from the supplied image path that will fit
        # within an area of 600px width and 400px height.
        {{ img_path|resize('600x400') }}

        # Resize and crop so that the image will fill the entire area
        {{ img_path|resize('300x300', fill=1) }}

        # Convert to JPG
        {{ img_path|resize('300x300', format='jpg') }}
    """
    _, _, filename = image_url.rpartition('/')
    resize_root = current_app.config['RESIZE_ROOT']
    resize_url = current_app.config['RESIZE_URL']
    root_relative_path = get_root_relative_path(image_url)
    width, height = parse_dimensions(dimensions)
    anchor = get_anchor(anchor)
    format = get_format(image_url, format)
    original_path = os.path.join(resize_root, root_relative_path)
    cache_path_args = root_relative_path.rpartition('/')[0].split('/')
    cache_path_args.extend([
        width or 'auto',
        height or 'auto',
        anchor.lower().replace('_', '-') if fill else '',
        'fill' if fill else 'no-fill',
        'upscale' if upscale else 'no-upscale',
    ])
    cache_path = get_relative_cache_path(filename, format.lower(),
                                         *cache_path_args)
    full_cache_url = os.path.join(resize_url, cache_path)
    full_cache_path = os.path.join(resize_root, cache_path)

    if fill and not all([width, height]):
        raise ValueError('Fill requires both width and height to be set.')

    if not os.path.exists(full_cache_path):
        generate_image(inpath=original_path, outpath=full_cache_path,
                       format=format, width=width, height=height,
                       upscale=upscale, fill=fill, anchor=anchor,
                       quality=quality, progressive=progressive)

    return full_cache_url


class Resize(object):
    """Adds a jinja filter for resizing images to the Flask template env"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if 'RESIZE_URL' not in app.config:
            raise RuntimeError('You must specify RESIZE_URL.')
        if 'RESIZE_ROOT' not in app.config:
            raise RuntimeError('You must specify RESIZE_ROOT.')

        resize_root = app.config['RESIZE_ROOT']

        if not os.path.isdir(resize_root):
            raise RuntimeError('Your RESIZE_ROOT does not exist or is a '
                               'regular file.')
        if not resize_root.endswith('/'):
            app.config['RESIZE_ROOT'] = resize_root + '/'

        app.config.setdefault('RESIZE_CACHE_DIR', 'cache')
        app.config.setdefault('RESIZE_HASH_FILENAME', True)
        app.config.setdefault('RESIZE_HASH_METHOD', 'md5')

        app.jinja_env.filters['resize'] = resize

    def teardown(self, exception):
        pass
