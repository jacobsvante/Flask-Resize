import hashlib
import io
import logging
import os

import pilkit.processors
import pilkit.utils
from flask import current_app
from PIL import Image, ImageColor, ImageDraw, ImageFont

from . import cache, constants, exc, storage, utils
from .configuration import Config
from ._compat import b, cairosvg

logger = logging.getLogger('flask_resize')


def format_to_ext(format):
    """Return the file extension to use for format"""
    return {
        constants.JPEG: 'jpg',
        constants.PNG: 'png',
        constants.SVG: 'svg',
    }[format]


def image_data(img, format, **save_options):
    """Save a PIL Image instance and return its byte contents"""
    fp = io.BytesIO()
    img.save(fp, format, **save_options)
    fp.seek(0)
    return fp.read()


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
    bgcolor = ImageColor.getrgb(utils.parse_rgb(bgcolor))
    processor = pilkit.processors.MakeOpaque(background_color=bgcolor)
    return processor.process(img)


def convert_svg(bdata):
    if cairosvg is None:
        raise exc.CairoSVGImportError(
            "CairoSVG must be installed for SVG input file support. "
            "Package found @ https://pypi.python.org/pypi/CairoSVG."
        )
    svg_data = cairosvg.svg2png(bytestring=bdata)
    return Image.open(io.BytesIO(svg_data))


def create_placeholder_image(width=None, height=None, message=None):
    """Create a placeholder image that specified its width and height, and an optional text.

    Args:
        width (Optional[:class:`str`]):
            Width to use for the image. Will use `height` if not provided.
        height (Optional[:class:`str`]):
            Height to use for the image. Will use `width` if not provided.
        message (Optional[:class:`str`]):
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
    if message is not None:
        placeholder_text += u' ({})'.format(message)
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


class ResizeTarget:

    def __init__(
        self,
        image_store,
        source_image_relative_url,
        dimensions=None,
        format=None,
        quality=80,
        fill=False,
        bgcolor=None,
        upscale=True,
        progressive=True,
        name_hashing_method=constants.DEFAULT_NAME_HASHING_METHOD,
        cache_store=cache.NoopCache(),
        target_directory=constants.DEFAULT_TARGET_DIRECTORY,
        use_placeholder=False,
    ):
        self.source_image_relative_url = source_image_relative_url
        self.use_placeholder = use_placeholder
        self.width, self.height = (
            utils.parse_dimensions(dimensions) if dimensions is not None
            else (None, None)
        )
        self.format = utils.parse_format(source_image_relative_url, format)
        self.quality = quality
        self.fill = fill
        self.bgcolor = (
            utils.parse_rgb(bgcolor, include_number_sign=False)
            if bgcolor is not None else None
        )
        self.upscale = upscale
        self.progressive = progressive
        self.name_hashing_method = name_hashing_method
        self.target_directory = target_directory

        self.image_store = image_store
        self.cache_store = cache_store

        self._validate_arguments()
        self.unique_key = self._generate_unique_key()

    def _validate_arguments(self):
        if not self.source_image_relative_url and not self.use_placeholder:
            raise exc.EmptyImagePathError()
        if self.fill and not all([self.width, self.height]):
            raise exc.MissingDimensionsError(
                'Fill requires both width and height to be set.'
            )

    @property
    def file_extension(self):
        return format_to_ext(self.format)

    def _get_generate_unique_key_args(self):
        return [
            self.source_image_relative_url,
            self.format,
            self.quality if self.format == constants.JPEG else '',
            self.width or 'auto',
            self.height or 'auto',
            'fill' if self.fill else '',
            'fill' if self.fill else 'no-fill',
            'upscale' if self.upscale else 'no-upscale',
            self.bgcolor or '',
        ]

    def _generate_unique_key(self):
        cache_key_args = self._get_generate_unique_key_args()
        hash = hashlib.new(self.name_hashing_method)
        hash.update(b(''.join(str(a) for a in cache_key_args)))
        name = hash.hexdigest()
        return '.'.join([
            '/'.join([self.target_directory, name]),
            self.file_extension
        ])

    def get_cached_path(self):
        if self.cache_store.exists(self.unique_key):
            logger.debug('Fetched from cache: {}'.format(self.unique_key))
            return self.unique_key
        else:
            msg = '`{}` is not cached.'.format(self.unique_key)
            logger.debug(msg)
            raise exc.CacheMiss(msg)

    def get_path(self):
        if self.image_store.exists(self.unique_key):
            # As the generated image might've been created on another instance,
            # we'll store the path in cache key here so we won't have to
            # manually check the path again.
            self.cache_store.add(self.unique_key)

            logger.debug('Found non-cached image: {}'.format(self.unique_key))
            return self.unique_key
        else:
            raise exc.ImageNotFoundError(self.unique_key)

    def get_generated_image(self):
        return self.image_store.get(self.unique_key)

    @property
    def source_format(self):
        if not self.source_image_relative_url:
            # Missing path means only a placeholder could be generated
            return constants.PNG
        else:
            fmt = os.path.splitext(self.source_image_relative_url)[1]
            assert fmt.startswith('.')
            return fmt[1:].upper()

    def _generate_impl(self):
        try:
            source_data = self.image_store.get(
                self.source_image_relative_url
            )
        except exc.ImageNotFoundError:
            if self.use_placeholder:
                source_data = self.generate_placeholder(
                    'Source image `{}` not found'.format(
                        self.source_image_relative_url
                    )
                )
            else:
                raise

        if self.source_format == constants.SVG:
            img = convert_svg(source_data)
        else:
            fp = io.BytesIO(source_data)
            img = Image.open(fp)

        if self.width or self.height:
            resize_to_fit_kw = dict(
                width=self.width,
                height=self.height,
                upscale=self.upscale
            )
            if self.fill:
                if self.bgcolor:
                    mat_color = ImageColor.getrgb(self.bgcolor)
                elif self.format == constants.JPEG:
                    mat_color = (255, 255, 255, 255)  # White
                else:
                    mat_color = (0, 0, 0, 0)  # Transparent
                resize_to_fit_kw['mat_color'] = mat_color

            processor = pilkit.processors.ResizeToFit(**resize_to_fit_kw)
            img = processor.process(img)

        options = {
            'icc_profile': img.info.get('icc_profile'),
        }

        if self.format == constants.JPEG:
            options.update(
                quality=int(self.quality),
                progressive=self.progressive
            )

        if self.bgcolor is not None:
            img = make_opaque(img, self.bgcolor)

        img, save_kwargs = pilkit.utils.prepare_image(img, self.format)
        save_kwargs.update(options)
        options = save_kwargs

        return image_data(img, self.format, **options)

    def generate(self):
        with self.cache_store.transaction(
            self.unique_key
        ) as transaction_successful:

            if transaction_successful:
                logger.info('Generating image: {}'.format(self.unique_key))
            else:
                logger.error(
                    'GenerateInProgress error for: {}'.format(self.unique_key)
                )
                raise exc.GenerateInProgress(self.unique_key)

            try:
                data = self._generate_impl()
                self.image_store.save(self.unique_key, data)
            except Exception as e:
                logger.info(
                    'Exception occurred - removing {} from cache and '
                    'image store. Exception was: {}'
                    .format(self.unique_key, e)
                )

                try:
                    self.image_store.delete(self.unique_key)
                except Exception as e2:
                    logger.warning(
                        'Another exception occurred while doing error cleanup '
                        'for: {}. The exception was: {}'
                        .format(self.unique_key, e2)
                    )
                    pass

                self.cache_store.remove(self.unique_key)

                raise e
            else:
                self.cache_store.add(self.unique_key)
            return data

    def generate_placeholder(self, message):
        img = create_placeholder_image(self.width, self.height, message)
        return image_data(img, 'PNG')


class Resizer:
    """Factory for creating the resize function"""

    def __init__(
        self,
        storage_backend,
        cache_store,
        base_url,
        name_hashing_method=constants.DEFAULT_NAME_HASHING_METHOD,
        target_directory=constants.DEFAULT_TARGET_DIRECTORY,
        raise_on_generate_in_progress=False,
        noop=False
    ):
        self.storage_backend = storage_backend
        self.cache_store = cache_store
        self.base_url = base_url
        self.name_hashing_method = name_hashing_method
        self.target_directory = target_directory
        self.raise_on_generate_in_progress = raise_on_generate_in_progress
        self.noop = noop
        self._fix_base_url()

    def _fix_base_url(self):
        if not self.base_url.endswith('/'):
            self.base_url += '/'

    def __call__(
        self,
        image_url,
        dimensions=None,
        format=None,
        quality=80,
        fill=False,
        bgcolor=None,
        upscale=True,
        progressive=True,
        placeholder=False
    ):
        """Method for resizing, converting and caching images

        Args:
            image_url (str):
                URL for the image to resize. A URL relative to `base_url`
            dimensions (str, Sequence[:class:`int`, :class:`int`]):
                Width and height to use when generating the new image.
                Uses the format of :func:`parse_dimensions`. No resizing
                is done if None is passed in.
            format (Optional[:class:`str`]):
                Format to convert into. Defaults to using the same format as the
                original image. An exception to this default is when the source
                image is of type SVG/SVGZ, then PNG is used as default.
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
                output format. Defaults to True.
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

        Usage:
            Generate an image from the supplied image URL that will fit
            within an area of 600px width and 400px height::

                resize('somedir/kittens.png', '600x400')

            Resize and crop so that the image will fill the entire area::

                resize('somedir/kittens.png', '300x300', fill=1)

            Convert to JPG::

                resize('somedir/kittens.png', '300x300', format='jpg')
        """

        if self.noop:
            return image_url

        if image_url and image_url.startswith(self.base_url):
            image_url = image_url[len(self.base_url):]

        target = ResizeTarget(
            self.storage_backend,
            image_url,
            dimensions=dimensions,
            format=format,
            quality=quality,
            fill=fill,
            bgcolor=bgcolor,
            upscale=upscale,
            progressive=progressive,
            use_placeholder=placeholder,
            cache_store=self.cache_store,
            name_hashing_method=self.name_hashing_method,
            target_directory=self.target_directory,
        )

        try:
            relative_url = target.get_cached_path()
        except exc.CacheMiss:
            try:
                relative_url = target.get_path()
            except exc.ImageNotFoundError:
                target.generate()
                relative_url = target.get_path()
            except exc.GenerateInProgress:
                if self.raise_on_generate_in_progress:
                    raise
                else:
                    relative_url = target.unique_key

        return os.path.join(self.base_url, relative_url)


def make_resizer(config):
    """Resizer instance factory"""
    return Resizer(
        storage_backend=storage.make(config),
        cache_store=cache.make(config),
        base_url=config.url,
        name_hashing_method=config.hash_method,
        target_directory=config.target_directory,
        raise_on_generate_in_progress=config.raise_on_generate_in_progress,
        noop=config.noop,
    )


class Resize(object):
    """
    Used for initializing the configuration needed for the ``Resizer``
    instance, and for the jinja filter to work in the flask app.

    Args:
        app (Any[flask.Flask, None]):
            A Flask app can be passed in immediately if not using the app
            factory pattern.
    """

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def __call__(self, *args, **kwargs):
        return current_app.resize(*args, **kwargs)

    def init_app(self, app):
        """Initialize Flask-Resize

        Args:
            app (:class:`flask.Flask`):
                The Flask app to configure.

        Raises:
            RuntimeError:
                A setting wasn't specified, or was invalid.
        """

        config = Config.from_dict(
            app.config,
            default_overrides={
                'RESIZE_RAISE_ON_GENERATE_IN_PROGRESS': app.debug,
            }
        )

        app.resize = app.jinja_env.filters['resize'] = make_resizer(config)
