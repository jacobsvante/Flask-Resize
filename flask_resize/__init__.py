import warnings
import errno
import hashlib
import os
import re
from pilkit.processors import Anchor, ResizeToFit, MakeOpaque
from pilkit.utils import save_image
from flask import current_app
from PIL import Image, ImageDraw, ImageFont, ImageColor
from .metadata import __version_info__, __version__  # NOQA
from ._compat import b, string_types
from . import exc

JPEG = 'JPEG'
PNG = 'PNG'


def parse_dimensions(dimensions):
    """Parse the Flask-Resize image dimensions format string/2-tuple

    Args:
        dimensions (:class:`str`, Sequence[:class:`int`]):
            Can be a string in format ``<width>x<height>``, ``<width>``,
            ``<width>x``, or ``x<height>``. Or a 2-tuple of ints containg
            width and height.

    Raises:
        :class:`exc.InvalidDimensionsError`:
            If the dimensions couldn't be parsed.
        :class:`exc.MissingDimensionsError`:
            If no width or height could be parsed from the string.

    Returns:
        Tuple[:class:`int`, :class:`int`]:
            Width and height.
    """

    if isinstance(dimensions, string_types):
        dims = dimensions.split('x')
        if len(dims) == 1:
            dims.append(None)
        dims = [d or None for d in dims]

    else:
        dims = [i for i in dimensions]

    if not any(dims) or len(dims) < 2:
        raise exc.MissingDimensionsError(dimensions)
    if len(dims) > 2:
        raise exc.InvalidDimensionsError(dimensions)

    return tuple((int(d) if d else None) for d in dims)


def _extract_relative_path(base_url, image_path):
    """Extract path relative to the base url, without leading slash

    Args:
        base_url (str):
            The base url to remove
        image_path (str):
            Path that may or may not start with ``base_url``

    Returns:
        str:
            The relative path
    """

    if image_path.startswith(base_url):
        image_path = image_path[len(base_url):]

    return image_path[1:] if image_path.startswith('/') else image_path


def _construct_relative_cache_path(filename, ext, *path_parts, **opts):
    """Construct a path to use for the cached version of a generated image

    If the app setting `RESIZE_HASH_FILENAME` is True (default) then a hash
    will be created of this. If False then the returned path will contain one
    sub-directory per item in *path_parts.

    Args:
        filename (str):
            The name of the file, excluding its extension
        ext (str):
            The file extension to use for the generated image
        *path_parts (Sequence[:class:`str`]):
            A sequence of strings to use as a unique identifier for the image.
            Usually image settings such as width, height, format etc.

    Returns:
        str:
            The path to save the cached image to
    """
    cache_dir = opts.pop('cache_dir', 'cache')
    hash_filename = opts.pop('hash_filename', True)
    hash_method = opts.pop('hash_method', 'md5')
    filename_no_ext, _, _ = filename.rpartition('.')
    filename = u'.'.join((filename_no_ext, ext))
    cache_path = u'/'.join(_strip_str(str(p)) for p in filter(None, path_parts))

    if hash_filename:
        hash = hashlib.new(hash_method)
        hash.update(b(cache_path + filename))
        s = u'{0}/{1}.{2}'.format(cache_dir, hash.hexdigest(), ext)
    else:
        s = os.path.join(cache_dir, cache_path, filename)
    return s


def _parse_anchor(value):
    """Get the Anchor constant from string

    Args:
        value (str):
            The value to turn into an Anchor. "top_left" becomes "tl".

    Raises:
        :class:`exc.InvalidResizeSettingError`:
            If an invalid anchor value was passed.

    Returns:
        str:
            The Anchor value (such as Anchor.TOP_LEFT which is 'tl')
    """
    valid_anchor_values = [a for a in vars(Anchor) if a[0].isupper()]
    anchor_attr = value.upper().replace('-', '_')
    if anchor_attr not in valid_anchor_values:
        raise exc.InvalidResizeSettingError(
            'Not a valid anchor value. Valid ones '
            'are {0}'.format(valid_anchor_values)
        )
    return getattr(Anchor, anchor_attr)


def _mkdir_p(path):
    """Creates all non-existing directories encountered in the passed in path

    Args:
        path (str):
            Path containing directories to create

    Raises:
        OSError:
            If some underlying error occurs when calling :func:`os.makedirs`,
            that is not errno.EEXIST.
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def _parse_format(image_path, format=None):
    """Parse and validate format from the supplied image path

    Args:
        image_path (str):
            Image path to parse format from
        format (Optional[:class:`str`]):
            This format is assumed if argument is not None

    Raises:
        :class:`exc.UnsupportedImageFormatError`:
            If an unsupported image format was encountered.

    Returns:
        str:
            Format of supplied image
    """
    if not format:
        _, _, format = image_path.rpartition('.')
    format = format.upper()
    if format == 'JPG':
        format = JPEG
    if format not in (JPEG, PNG):
        raise exc.UnsupportedImageFormatError(
            "JPEG and PNG are the only supported formats at the moment."
        )
    return format


def _get_package_path(relpath):
    """Get the full path for a file within the package

    Args:
        relpath (str):
            A path contained within the flask_resize

    Returns:
        str: Full path for the file requested
    """
    pkgdir = os.path.dirname(__file__)
    return os.path.join(pkgdir, 'fonts', relpath)


def create_placeholder_img(width=None, height=None, placeholder_reason=None):
    """Create a placeholder image that specified its width and height, and an optional text.

    Args:
        width (Optional[:class:`str`]):
            Width to use for the image. Will use `height` if not provided.
        height (Optional[:class:`str`]):
            Height to use for the image. Will use `width` if not provided.
        placeholder_reason (Optional[:class:`str`]):
            Text to add to the center of the placeholder image.

    Raises:
        :class:`exc.MissingDimensionsError`:
            If neither `width` nor `height` are provided.

    Returns:
        PIL.Image:
            The placeholder image.
    """
    if width is None and height is None:
        raise exc.MissingDimensionsError("Specify at least one of `width` "
                                         "or `height`")
    placeholder_width = width or height
    placeholder_height = height or width
    placeholder_text = '{}x{}'.format(placeholder_width,
                                      placeholder_height)
    if placeholder_reason is not None:
        placeholder_text += u' ({})'.format(placeholder_reason)
    text_fill = (255, ) * 3
    bg_fill = (220, ) * 3
    img = Image.new('RGB', (placeholder_width, placeholder_height), bg_fill)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(_get_package_path('DroidSans.ttf'), size=36)
    text_width, text_height = draw.textsize(placeholder_text, font=font)
    draw.text((((placeholder_width - text_width) / 2),
               ((placeholder_height - text_height) / 2)),
              text=placeholder_text, font=font, fill=text_fill)
    del draw
    return img


def parse_rgb(v, include_number_sign=True):
    """Create a hex value color representation of the provided value

    Args:
        v (:class:`str`, Sequence[:class:`int`, :class:`int`, :class:`int`]):
            A RGB color value in hex representation, may or may not start
            with a number sign ("#"). Can be in short CSS format with only
            three characters, or the regular six character length.
            Can also a 3-tuple of integers, representing Red, Green and Blue.
        include_number_sign (bool):
            Whether or not to prepend a number sign to the output string.

    Returns:
        str:
            A full hex representation of the passed in RGB value
    """
    if isinstance(v, tuple):
        v = ''.join('{:02x}'.format(d) for d in v)
    if v.startswith('#'):
        v = v[1:]
    if len(v) == 3:
        v = u''.join(s + s for s in v)
    return u'#' + v if include_number_sign else v


def make_opaque(img, bgcolor):
    """Apply a background color to image

    Args:
        img (PIL.Image):
            Image to alter.
        bgcolor (str):
            A :func:`parse_rgb` parseable value to use as background color.

    Returns:
        PIL.Image:
            A new image with the background color applied.
    """
    bgcolor = ImageColor.getrgb(parse_rgb(bgcolor))
    processor = MakeOpaque(background_color=bgcolor)
    return processor.process(img)


def generate_image(inpath, outpath, width=None, height=None, format=JPEG,
                   fill=False, upscale=True, anchor=None, quality=80,
                   bgcolor=None, progressive=True, placeholder_reason=None):
    """Generate an image with the passed in settings
    This is used by :func:`resize` and is run outside of the Flask context.

    Args:
        inpath (str):
            Path to the image to generate a new image out of.
        outpath (str):
            Where the new image will end up.
        width (Optional[:class:`int`]):
            The width to use for the generated image.
        height (Optional[:class:`str`]):
            The height to use for the generated image.
        format (str):
            Format to convert into. Defaults to "JPEG".
        fill (bool):
            Fill the entire width and height that was specified if True,
            otherwise keep the original image dimensions. Defaults to False.
        upscale (bool):
            Whether or not to allow the image to become bigger than the
            original if the request width and/or height is bigger than its
            dimensions. Defaults to True.
        anchor (str):
            Deprecated since Flask-Resize 0.6.
        quality (int):
            Quality of the output image, if the format is JPEG. Defaults to 80.
        bgcolor (Optional[:class:`str`]):
            If specified this color will be used as background.
        progressive (bool):
            Whether to use progressive encoding or not when JPEG is the
            output format.
        placeholder_reason (Optional[:class:`str`]):
            A text to show the user if the image path could not be found.

    Raises:
        :class:`exc.ImageNotFoundError`:
            If the source image cannot be found or is not a file.

    Returns:
        PIL.Image:
            The generated image.
    """
    if anchor:
        warnings.warn(
            "anchor has been deprecated in Flask-Resize 0.6 and doesn't do anything to the image. Will be removed in 1.0.",
            DeprecationWarning
        )

    _mkdir_p(outpath.rpartition('/')[0])
    if not os.path.isfile(inpath):
        if placeholder_reason:
            img = create_placeholder_img(width, height, placeholder_reason)
        else:
            raise exc.ImageNotFoundError(inpath)
    else:
        img = Image.open(inpath)
    processor_kwargs = dict(width=width, height=height, upscale=upscale)

    if fill:
        if bgcolor:
            mat_color = ImageColor.getrgb(parse_rgb(bgcolor))
        elif format == JPEG:
            mat_color = (255, 255, 255, 255)  # White
        else:
            mat_color = (0, 0, 0, 0)  # Transparent
        processor_kwargs['mat_color'] = mat_color  # Transparent

    processor = ResizeToFit(**processor_kwargs)
    img = processor.process(img)

    assert (not os.path.exists(outpath)), 'Path to save to already exists'

    options = {}
    if format == JPEG:
        options.update({'quality': int(quality), 'progressive': progressive})

    if bgcolor is not None:
        img = make_opaque(img, bgcolor)

    with open(outpath, 'wb') as outfile:
        save_image(img, outfile, format=format, options=options)
    return img


def _strip_str(s):
    """Strip non-letters/digits from passed in string.
    Args:
        s (str):
            The string to strip.

    Returns:
        str:
            A "safe" version of the passed in string.
    """
    return re.sub('\W', '-', s)


def safe_placeholder_filename(orig_filename, ext='png'):
    """Strip non-letters/digits from filename and append extension to filename.

    Args:
        orig_filename (str):
            The filename to make "safe", without file extension.
        ext (str):
            File extension to append to the filename

    Returns:
        str:
            A "safe" version of the passed in filename.
    """
    return '{}.{}'.format(_strip_str(orig_filename), ext)


def resize(image_url, dimensions, format=None, quality=80, fill=False,
           bgcolor=None, upscale=True, progressive=True, anchor='center',
           placeholder=False):
    """Jinja filter for resizing, converting and caching images.

    Args:
        image_url (str):
            URL for the image to resize.
        dimensions (str, Sequence[:class:`int`, :class:`int`]):
            Width and height to use when generating the new image.
            Uses the format of :func:`parse_dimensions`.
        format (Optional[:class:`str`]):
            Format to convert into. Defaults to using the same format as the
            original image.
        quality (int):
            Quality of the output image, if the format is JPEG. Defaults to 80.
        fill (bool):
            Fill the entire width and height that was specified if True,
            otherwise keep the original image dimensions. Defaults to False.
        bgcolor (Optional[:class:`str`]):
            If specified this color will be used as background.
        upscale (bool):
            Whether or not to allow the image to become bigger than the
            original if the request width and/or height is bigger than its
            dimensions. Defaults to True.
        progressive (bool):
            Whether to use progressive encoding or not when JPEG is the
            output format.
        anchor (str):
            Deprecated since Flask-Resize 0.6.
        placeholder (bool):
            Whether to show a placeholder if the specified ``image_url``
            couldn't be found.

    Raises:
        :class:`exc.EmptyImagePathError`:
            If an empty image path was received.
        :class:`exc.ImageNotFoundError`:
            If the image could not be found.
        :class:`exc.MissingDimensionsError`:
            If ``fill`` argument was True, but width or height was not passed.

    Returns:
        str:
            URL to the generated and cached image.

    Examples:
        Generate an image from the supplied image URL that will fit
        within an area of 600px width and 400px height::

            {{ original_image_url|resize('600x400') }}

        Resize and crop so that the image will fill the entire area::

            {{ original_image_url|resize('300x300', fill=1) }}

        Convert to JPG::

            {{ original_image_url|resize('300x300', format='jpg') }}
    """
    if current_app.config['RESIZE_NOOP']:
        return image_url

    use_placeholder = placeholder
    resize_root = current_app.config['RESIZE_ROOT']
    resize_url = current_app.config['RESIZE_URL']

    if not image_url:
        if use_placeholder:
            placeholder_reason = 'empty image path'
            image_url = 'empty-image-path'
        else:
            raise exc.EmptyImagePathError()
    else:
        placeholder_reason = None

    root_relative_path = _extract_relative_path(resize_url, image_url)
    original_path = os.path.join(resize_root, root_relative_path)

    if os.path.isfile(original_path):
        _, _, filename = image_url.rpartition('/')
        placeholder_reason = None
    else:
        if use_placeholder:
            placeholder_reason = u'"{}" does not exist.'.format(original_path)
            image_url = safe_placeholder_filename(placeholder_reason)
            filename = image_url
        else:
            raise exc.ImageNotFoundError(original_path)

    width, height = parse_dimensions(dimensions)
    anchor = _parse_anchor(anchor)
    format = _parse_format(image_url, format)
    cache_path_args = root_relative_path.rpartition('/')[0].split('/')
    cache_path_args.extend([
        str(quality) if format == JPEG else '',
        width or 'auto',
        height or 'auto',
        anchor.lower().replace('_', '-') if fill else '',
        'fill' if fill else 'no-fill',
        'upscale' if upscale else 'no-upscale',
        parse_rgb(bgcolor, include_number_sign=False) if bgcolor else '',
    ])

    cache_path = _construct_relative_cache_path(
        filename, format.lower(), *cache_path_args,
        cache_dir=current_app.config['RESIZE_CACHE_DIR'],
        hash_filename=current_app.config['RESIZE_HASH_FILENAME'],
        hash_method=current_app.config['RESIZE_HASH_METHOD'])

    full_cache_url = os.path.join(resize_url, cache_path)
    full_cache_path = os.path.join(resize_root, cache_path)

    if fill and not all([width, height]):
        raise exc.MissingDimensionsError('Fill requires both width and height '
                                         'to be set.')

    if not os.path.exists(full_cache_path):
        generate_image(inpath=original_path, outpath=full_cache_path,
                       format=format, width=width, height=height,
                       bgcolor=bgcolor, upscale=upscale, fill=fill,
                       anchor=anchor, quality=quality, progressive=progressive,
                       placeholder_reason=placeholder_reason)

    return full_cache_url


class Resize(object):
    """Used for initializing the ``resize`` jinja filter in the app.

    Examples:
        Set-up using the direct initialization::

            import flask
            import flask_resize

            app = flask.Flask(__name__)
            app.config['RESIZE_URL'] = 'https://mysite.com/'
            app.config['RESIZE_ROOT'] = '/home/user/myapp/images'

            flask_resize.Resize(app)

        Set-up using the app factory pattern::

            import flask
            import flask_resize

            resize = flask_resize.Resize()

            def create_app(**config_values):
                app = flask.Flask()
                app.config.update(**config_values)
                resize.init_app(app)
                return app

            # And later on...
            app = create_app(RESIZE_URL='https://mysite.com/',
                             RESIZE_ROOT='/home/user/myapp/images')
    """

    def __init__(self, app=None):
        """
        Args:
            app (Optional[:class:`flask.Flask`]):
                Flask app to configure thisinstance on. Only use this if
                you're not using an factory function to initialize the app.
        """
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize Flask-Resize

        Args:
            app (:class:`flask.Flask`):
                The Flask app to configure.

        Raises:
            RuntimeError:
                A setting wasn't specified, or was invalid.
        """
        app.jinja_env.filters['resize'] = resize
        app.config.setdefault('RESIZE_NOOP', False)
        app.config.setdefault('RESIZE_CACHE_DIR', 'cache')
        app.config.setdefault('RESIZE_HASH_FILENAME', True)
        app.config.setdefault('RESIZE_HASH_METHOD', 'md5')

        if app.config['RESIZE_NOOP']:
            return  # No RESIZE_URL or RESIZE_ROOT need to be specified.

        if not isinstance(app.config.get('RESIZE_URL'), string_types):
            raise RuntimeError('You must specify a valid RESIZE_URL.')
        if not isinstance(app.config.get('RESIZE_ROOT'), string_types):
            raise RuntimeError('You must specify a valid RESIZE_ROOT.')

        resize_root = app.config['RESIZE_ROOT']

        if not os.path.isdir(resize_root):
            raise RuntimeError('Your RESIZE_ROOT does not exist or is a '
                               'regular file.')
        if not resize_root.endswith('/'):
            app.config['RESIZE_ROOT'] = resize_root + '/'
