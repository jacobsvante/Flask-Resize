import hashlib
import io
import os.path as op

import pilkit.processors
import pilkit.utils
from PIL import Image, ImageDraw, ImageFont, ImageColor
from flask import current_app

from . import cache, constants, exc, storage, utils
from ._compat import b, cairosvg, redis, string_types


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
    pkgdir = op.dirname(__file__)
    return op.join(pkgdir, 'fonts', relpath)


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
        dimensions,
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
        self.width, self.height = utils.parse_dimensions(dimensions)
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

    @property
    def file_extension(self):
        return format_to_ext(self.format)

    def _generate_unique_key(self):
        cache_key_args = self._get_generate_unique_key_args()
        hash = hashlib.new(self.name_hashing_method)
        hash.update(b(''.join(str(a) for a in cache_key_args)))
        name = hash.hexdigest()
        return '.'.join([
            op.join(self.target_directory, name),
            self.file_extension
        ])

    def get_cached_path(self):
        if self.cache_store.exists(self.unique_key):
            return self.unique_key
        else:
            raise exc.CacheMiss('`{}` is not cached.'.format(self.unique_key))

    def get_path(self):
        if self.image_store.exists(self.unique_key):
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
            return self.source_image_relative_url.rpartition('.')[2].upper()

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

        processor_kwargs = dict(
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
            processor_kwargs['mat_color'] = mat_color

        processor = pilkit.processors.ResizeToFit(**processor_kwargs)
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
        if self.cache_store.exists(self.unique_key):
            raise exc.GenerateInProcess()

        # Add to cache before starting the generation, to deal with other
        # threads/processes starting generation of the same file. A common
        # example when this might happen is when multiple users hit the
        # same page at the same time - both server workers will initate
        # generation of the same file at the same time. When the redis
        # cache is enabled this will be extremely unlikely.
        self.cache_store.add(self.unique_key)

        try:
            data = self._generate_impl()
            self.image_store.save(self.unique_key, data)
        except:
            self.cache_store.remove(self.unique_key)
            raise
        return data

    def generate_placeholder(self, message):
        img = create_placeholder_image(self.width, self.height, message)
        return image_data(img, 'PNG')


def resize(image_url, dimensions, format=None, quality=80, fill=False,
           bgcolor=None, upscale=True, progressive=True, placeholder=False):
    """Jinja filter for resizing, converting and caching images.

    Args:
        image_url (str):
            URL for the image to resize. Can be a relative URL, or include the config's `RESIZE_URL` value.
        dimensions (str, Sequence[:class:`int`, :class:`int`]):
            Width and height to use when generating the new image.
            Uses the format of :func:`parse_dimensions`.
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

    if image_url and image_url.startswith(current_app.config['RESIZE_URL']):
        image_url = image_url[len(current_app.config['RESIZE_URL']):]

    target = ResizeTarget(
        current_app.resize_image_store,
        image_url,
        dimensions=dimensions,
        format=format,
        quality=quality,
        fill=fill,
        bgcolor=bgcolor,
        upscale=upscale,
        progressive=progressive,
        use_placeholder=placeholder,
        cache_store=current_app.resize_cache_store,
        name_hashing_method=current_app.config['RESIZE_HASH_METHOD'],
        target_directory=(
            current_app.config['RESIZE_TARGET_DIRECTORY']
        ),
    )

    try:
        relative_url = target.get_cached_path()
    except exc.CacheMiss:
        try:
            relative_url = target.get_path()
        except exc.ImageNotFoundError:
            target.generate()
            relative_url = target.get_path()

    return op.join(current_app.config['RESIZE_URL'], relative_url)


class Resize(object):
    """
    Used for initializing the configuration needed for the ``resize``
    function (and jinja filter) to work in a flask app.

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
        app.resize = app.jinja_env.filters['resize'] = resize
        app.config.setdefault('RESIZE_NOOP', False)
        app.config.setdefault(
            'RESIZE_TARGET_DIRECTORY',
            constants.DEFAULT_TARGET_DIRECTORY
        )
        app.config.setdefault(
            'RESIZE_CACHE_STORE',
            'redis' if redis is not None else None
        )
        app.config.setdefault('RESIZE_REDIS_HOST', 'localhost')
        app.config.setdefault('RESIZE_REDIS_PORT', 6379)
        app.config.setdefault('RESIZE_REDIS_DB', 0)

        # Note that only one key is set - a SET type, which is updated
        # with all the unique names of already generated files.
        app.config.setdefault('RESIZE_REDIS_KEY', constants.DEFAULT_REDIS_KEY)

        app.config.setdefault(
            'RESIZE_HASH_METHOD',
            constants.DEFAULT_NAME_HASHING_METHOD
        )
        app.config.setdefault('RESIZE_S3_ACCESS_KEY', None)
        app.config.setdefault('RESIZE_S3_SECRET_KEY', None)
        app.config.setdefault('RESIZE_S3_BUCKET', None)
        app.config.setdefault(
            'RESIZE_USE_S3',
            all([
                app.config['RESIZE_S3_ACCESS_KEY'],
                app.config['RESIZE_S3_SECRET_KEY'],
                app.config['RESIZE_S3_BUCKET'],
            ])
        )

        if app.config['RESIZE_NOOP']:
            return  # No RESIZE_URL or RESIZE_ROOT need to be specified.

        if app.config['RESIZE_USE_S3']:
            app.config['RESIZE_ROOT'] = None
            app.resize_image_store = storage.S3Storage(
                access_key=app.config['RESIZE_S3_ACCESS_KEY'],
                secret_key=app.config['RESIZE_S3_SECRET_KEY'],
                bucket=app.config['RESIZE_S3_BUCKET'],
            )
            app.config.setdefault(
                'RESIZE_URL',
                app.resize_image_store.base_url
            )
        else:
            if not isinstance(app.config.get('RESIZE_URL'), string_types):
                raise RuntimeError('You must specify a valid RESIZE_URL.')

            if not isinstance(app.config.get('RESIZE_ROOT'), string_types):
                raise RuntimeError('You must specify a valid RESIZE_ROOT.')
            if not op.isdir(app.config['RESIZE_ROOT']):
                raise RuntimeError(
                    'Your RESIZE_ROOT does not exist or is a regular file.'
                )
            if not app.config['RESIZE_ROOT'].endswith('/'):
                app.config['RESIZE_ROOT'] = app.config['RESIZE_ROOT'] + '/'

            app.resize_image_store = storage.FileStorage(
                base_path=app.config['RESIZE_ROOT'],
            )

        if app.config['RESIZE_CACHE_STORE'] == 'redis':
            kw = dict(
                host=app.config['RESIZE_REDIS_HOST'],
                port=app.config['RESIZE_REDIS_PORT'],
                db=app.config['RESIZE_REDIS_DB'],
                key=app.config['RESIZE_REDIS_KEY'],
            )
            app.resize_cache_store = cache.RedisCache(**kw)
        else:
            app.resize_cache_store = cache.NoopCache()

        if not app.config['RESIZE_URL'].endswith('/'):
            app.config['RESIZE_URL'] = app.config['RESIZE_URL'] + '/'
