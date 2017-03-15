import os

import pytest

import flask_resize as fr
from flask_resize._compat import boto3

from ._mocking import mock_s3


def test_file_storage(filestorage, tmpdir):

    filepath1 = tmpdir.join('file1.txt')
    filepath1.write('content')
    data = filestorage.get(str(filepath1))
    assert data == b'content'

    filepath2 = tmpdir.join('file2.txt')
    filestorage.save(str(filepath2), b'content')
    data = filestorage.get(str(filepath2))
    assert data == b'content'

    with pytest.raises(fr.exc.FileExistsError):
        filestorage.save(str(filepath2), b'')

    filestorage.delete(str(filepath2))

    with pytest.raises(OSError) as excinfo:
        filestorage.delete(str(filepath2))
    assert excinfo.value.errno == 2


@mock_s3
@pytest.mark.skipif(
    boto3 is None,
    reason='`boto3` has to be installed to run this test'
)
def test_s3_storage():
    real_access_key = os.environ.get('RESIZE_S3_ACCESS_KEY')
    real_secret_key = os.environ.get('RESIZE_S3_SECRET_KEY')
    real_bucket_name = os.environ.get('RESIZE_S3_BUCKET')
    s3_storage = fr.storage.S3Storage(
        access_key=real_access_key or 'test-access-key',
        secret_key=real_secret_key or 'test-secret-key',
        bucket=real_bucket_name or 'test-bucket',
    )

    if not real_bucket_name:
        # Create mock bucket
        conn = boto3.resource('s3', region_name='eu-central-1')
        conn.create_bucket(Bucket='test-bucket')

    assert s3_storage.base_url.startswith('https://s3.')
    assert s3_storage.base_url.endswith(
        '.amazonaws.com/' + (real_bucket_name or 'test-bucket')
    )

    # In case it already exists
    s3_storage.delete('file1.txt')

    assert s3_storage.exists('file1.txt') is False

    s3_storage.save('file1.txt', b'content')
    data = s3_storage.get('file1.txt')

    assert s3_storage.exists('file1.txt') is True
    assert data == b'content'

    # Cleanup
    s3_storage.delete('file1.txt')
