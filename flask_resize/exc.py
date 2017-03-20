from ._compat import FileExistsError  # noqa


class InvalidResizeSettingError(ValueError):
    """Raised when a resize argument such as if `width` was invalid."""


class EmptyImagePathError(InvalidResizeSettingError):
    """Raised if an empty image path was encountered."""


class InvalidDimensionsError(InvalidResizeSettingError):
    """Raised when a dimension string/tuple is improperly specified."""


class MissingDimensionsError(InvalidDimensionsError):
    """Raised when width and/or height is missing."""


class UnsupportedImageFormatError(InvalidResizeSettingError):
    """Raised when an unsupported output image format is encountered."""


class ImageNotFoundError(IOError):
    """Raised if the image could not be fetched from storage."""


class CacheMiss(RuntimeError):
    """Raised when a cached image path could not be found"""


class GenerateInProgress(RuntimeError):
    """The image is currently being generated"""


class CairoSVGImportError(ImportError):
    """Raised when an SVG input file is encountered but CairoSVG is not installed."""


class RedisImportError(ImportError):
    """Raised when Redis cache is configured, but the `redis` library is not installed."""


class Boto3ImportError(ImportError):
    """Raised when S3 is configured, but the `boto3` library is not installed."""
