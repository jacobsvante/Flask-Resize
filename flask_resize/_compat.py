import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,

    def b(s):
        return s.encode("latin-1")

else:
    string_types = basestring,  # noqa

    def b(s):
        return s


try:
    import cairosvg
except ImportError:
    cairosvg = None


try:
    import redis
except ImportError:
    redis = None


try:
    import boto3
    import botocore
except ImportError:
    boto3 = None
    botocore = None


try:
    FileExistsError = FileExistsError
except NameError:
    class FileExistsError(IOError):
        pass
