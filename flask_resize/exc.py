class InvalidResizeSettingError(ValueError):
    """Raised when a resize argument such as `anchor` or `width` was invalid."""


class EmptyImagePathError(InvalidResizeSettingError):
    """Raised if an empty image path was encountered."""


class ImageNotFoundError(InvalidResizeSettingError):
    """Raised if an image could not be found."""


class InvalidDimensionsError(InvalidResizeSettingError):
    """Raised when a dimension string/tuple is improperly specified."""


class MissingDimensionsError(InvalidDimensionsError):
    """Raised when width and/or height is missing."""


class UnsupportedImageFormatError(InvalidResizeSettingError):
    """Raised when an unsupported image format is encountered."""
