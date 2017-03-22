import errno
import itertools
import os

from . import constants, exc
from ._compat import string_types


def mkdir_p(path):
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


def parse_format(image_path, format=None):
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
        format = os.path.splitext(image_path)[1][1:]
    format = format.upper()
    if format in ('JPEG', 'JPG'):
        format = constants.JPEG
    if format == constants.SVG:
        format = constants.PNG
    if format not in constants.SUPPORTED_OUTPUT_FILE_FORMATS:
        raise exc.UnsupportedImageFormatError(
            "JPEG and PNG are the only supported output "
            "file formats at the moment."
        )
    return format


def chunked(iterable, size):
    """Split iterable `iter` into one or more `size` sized tuples"""
    it = iter(iterable)
    return iter(lambda: tuple(itertools.islice(it, size)), ())
