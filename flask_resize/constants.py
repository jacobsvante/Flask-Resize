DEFAULT_NAME_HASHING_METHOD = 'sha1'
"""Default filename hashing method for generated images"""

DEFAULT_TARGET_DIRECTORY = 'resized-images'
"""Default target directory for generated images"""

DEFAULT_REDIS_KEY = 'flask-resize'
"""Default key to store redis cache as"""

JPEG = 'JPEG'
"""JPEG format"""

PNG = 'PNG'
"""PNG format"""

SVG = 'SVG'
"""SVG format"""

SUPPORTED_OUTPUT_FILE_FORMATS = (JPEG, PNG)
"""Image formats that can be generated"""
