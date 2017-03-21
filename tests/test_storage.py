import os

import pytest

import flask_resize
from flask_resize._compat import boto3

from ._mocking import mock_s3
from .decorators import requires_boto3


def test_file_storage(filestorage, tmpdir):
    basepath = tmpdir.mkdir('subdir')
    tmpdir.mkdir('subdir/subsubdir')

    filepath1 = basepath.join('file1.txt')
    filepath1.write('content')
    data = filestorage.get('subdir/file1.txt')
    assert data == b'content'

    with pytest.raises(flask_resize.exc.FileExistsError):
        filestorage.save('subdir/file1.txt', b'')

    filestorage.delete('subdir/file1.txt')

    with pytest.raises(OSError) as excinfo:
        filestorage.delete('subdir/file1.txt')
    assert excinfo.value.errno == 2

    filestorage.save('subdir/file2.txt', b'content2')
    filestorage.save('subdir/subsubdir/file3.txt', b'content3')

    expected_relpaths = set(['subdir/file2.txt', 'subdir/subsubdir/file3.txt'])

    assert set(filestorage.list_tree('subdir')) == expected_relpaths
    assert set(filestorage.delete_tree('subdir')) == expected_relpaths
    assert list(filestorage.delete_tree('subdir')) == []


@mock_s3
@requires_boto3
def test_s3_storage():
    real_access_key = os.environ.get('RESIZE_S3_ACCESS_KEY')
    real_secret_key = os.environ.get('RESIZE_S3_SECRET_KEY')
    real_bucket_name = os.environ.get('RESIZE_S3_BUCKET')
    s3_storage = flask_resize.storage.S3Storage(
        real_bucket_name or 'test-bucket',
        access_key=real_access_key,
        secret_key=real_secret_key,
        region_name='eu-central-1',
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
    s3_storage.delete('subdir/file1.txt')

    assert s3_storage.exists('subdir/file1.txt') is False

    s3_storage.save('subdir/file1.txt', b'content')
    data = s3_storage.get('subdir/file1.txt')

    assert s3_storage.exists('subdir/file1.txt') is True
    assert data == b'content'

    # Cleanup
    s3_storage.delete('subdir/file1.txt')

    s3_storage.save('subdir/file2.txt', b'content2')
    s3_storage.save('subdir/subsubdir/file3.txt', b'content3')

    expected_relpaths = set(['subdir/file2.txt', 'subdir/subsubdir/file3.txt'])

    assert set(s3_storage.list_tree('subdir')) == expected_relpaths
    assert set(s3_storage.delete_tree('subdir')) == expected_relpaths
    assert list(s3_storage.delete_tree('subdir')) == []
