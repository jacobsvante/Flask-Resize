import os

test_real_s3_keys = (
    'RESIZE_S3_ACCESS_KEY',
    'RESIZE_S3_SECRET_KEY',
    'RESIZE_S3_BUCKET',
)

if 'RESIZE_S3_BUCKET' in os.environ:
    def mock_s3(f):
        return f
else:
    try:
        from moto import mock_s3
    except ImportError:
        def mock_s3(f):
            return f
