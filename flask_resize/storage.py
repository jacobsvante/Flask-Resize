import os

from . import exc, utils
from ._compat import PY2, boto3, botocore, string_types


def make(config):
    """Generate storage backend from supplied config

    Args:
        config (dict):
            The config to extract settings from

    Returns:
        Any[FileStorage, S3Storage]:
            A :class:`Storage` sub-class, based on the `RESIZE_STORAGE_BACKEND`
            value.

    Raises:
        RuntimeError: If another `RESIZE_STORAGE_BACKEND` value was set
    """

    if config.noop:
        config.url = '/'
        return None

    elif config.storage_backend == 's3':
        if not config.s3_bucket:
            raise RuntimeError(
                'You must specify RESIZE_S3_BUCKET when '
                'RESIZE_STORAGE_BACKEND is set to "s3".'
            )

        store = S3Storage(
            access_key=config.s3_access_key,
            secret_key=config.s3_secret_key,
            bucket=config.s3_bucket,
            region_name=config.s3_region,
        )
        config.url = store.base_url

    elif config.storage_backend == 'file':
        if not isinstance(config.url, string_types):
            raise RuntimeError(
                'You must specify a valid RESIZE_URL '
                'when RESIZE_STORAGE_BACKEND is set to "file".'
            )

        if not isinstance(config.root, string_types):
            raise RuntimeError(
                'You must specify a valid RESIZE_ROOT '
                'when RESIZE_STORAGE_BACKEND is set to "file".'
            )
        if not os.path.isdir(config.root):
            raise RuntimeError(
                'Your RESIZE_ROOT does not exist or is a regular file.'
            )
        if not config.root.endswith(os.sep):
            config.root = config.root + os.sep

        store = FileStorage(base_path=config.root)

    else:
        raise RuntimeError(
            'Non-supported RESIZE_STORAGE_BACKEND value: "{}"'
            .format(config.storage_backend)
        )

    return store


class Storage:
    """Storage backend base class"""

    def __init__(self, *args, **kwargs):
        pass

    def get(self, relative_path):
        raise NotImplementedError

    def save(self, relative_path, bdata):
        raise NotImplementedError

    def exists(self, relative_path):
        raise NotImplementedError

    def delete(self, relative_path):
        raise NotImplementedError

    def list_tree(self, subdir):
        raise NotImplementedError

    def delete_tree(self, subdir):
        raise NotImplementedError


class FileStorage(Storage):
    """Local file based storage

    Note that to follow the same convention as for `S3Storage`, all
    methods' passed in and extracted paths must use forward slash as
    path separator. the path separator. The only exception is the `base_path`
    passed in to the constructor.

    Args:
        base_path (str): The directory where files will be read from and written to. Expected to use the local OS's path separator.

    """

    def __init__(self, base_path):
        self.base_path = base_path

    def _get_full_path(self, key):
        """
        Replaces key with OS specific path separator and joins with `base_path`

        Args:
            key (str): The key / relative file path to make whole

        Returns:
            str: The full path
        """
        key = key.replace('/', os.sep)
        return os.path.join(self.base_path, key)

    def get(self, key):
        """Get binary file data for specified key

        Args:
            key (str): The key / relative file path to get data for

        Returns:
            bytes: The file's binary data
        """
        if not key:
            raise exc.ImageNotFoundError()
        path = self._get_full_path(key)
        try:
            with open(path, 'rb') as fp:
                return fp.read()
        except IOError as e:
            if e.errno == 2:
                raise exc.ImageNotFoundError(*e.args)
            else:
                raise

    def save(self, key, bdata):
        """Store binary file data at specified key

        Args:
            key (str): The key / relative file path to store data at
            bdata (bytes): The file data
        """
        full_path = self._get_full_path(key)
        utils.mkdir_p(os.path.split(full_path)[0])

        # Python 2 doesn't natively support `xb` mode as used below. Have to
        # manually check for the file's existence.
        if PY2 and self.exists(key):
            raise exc.FileExistsError(17, 'File exists')
        with open(full_path, 'wb' if PY2 else 'xb') as fp:
            fp.write(bdata)

    def exists(self, key):
        """Check if the key exists in the backend

        Args:
            key (str): The key / relative file path to check

        Returns:
            bool: Whether the file exists or not
        """
        if not key:
            return False
        full_path = self._get_full_path(key)
        return os.path.exists(full_path)

    def delete(self, key):
        """Delete file at specified key

        Args:
            key (str): The key / relative file path to delete
        """
        os.remove(self._get_full_path(key))

    def list_tree(self, subdir):
        """
        Recursively yields all regular files' names in a sub-directory of the
        storage backend.

        Keys/filenames are returned `self.base_path`-relative, and uses
        forward slash as a path separator, regardless of OS.

        Args:
            subdir (str):
                The subdirectory to list paths for

        Returns:
            Generator[str, str, None]:
                Yields subdirectory's filenames
        """
        assert subdir, 'Subdir must be specified'
        base_path = self.base_path
        if not base_path.endswith(os.sep):
            base_path += os.sep
        tree_base = os.path.join(base_path, subdir)
        for root, dirs, filenames in os.walk(tree_base, topdown=False):
            for filename in filenames:
                root_relative_path = root[len(base_path):].replace(os.sep, '/')
                relative_path = '/'.join([root_relative_path, filename])
                yield relative_path

    def delete_tree(self, subdir):
        """
        Recursively deletes all regular files in specified sub-directory

        Args:
            subdir (str):
                The subdirectory to delete files in

        Returns:
            Generator[str, str, None]:
                Yields deleted subdirectory's filenames
        """
        for relative_path in self.list_tree(subdir):
            full_path = self._get_full_path(relative_path)
            os.remove(full_path)
            yield relative_path


class S3Storage(Storage):
    """
    Amazon Web Services S3 based storage

    Args:
        bucket (str): Bucket name
        access_key (Any[str, None]): The access key. Defaults to reading from the local AWS config.
        secret_key (Any[str, None]): The secret access key. Defaults to reading from the local AWS config.
        region_name (Any[str, None]): The name of the bucket's region. Defaults to reading from the local AWS config.
        file_acl (str):
            The ACL to set on uploaded images. Defaults to "public-read"

    """

    def __init__(
        self,
        bucket,
        access_key=None,
        secret_key=None,
        region_name=None,
        file_acl='public-read'
    ):
        if boto3 is None:
            raise exc.Boto3ImportError(
                "boto3 must be installed for Amazon S3 support. "
                "Package found @ https://pypi.python.org/pypi/boto3."
            )
        default_session = botocore.session.get_session()
        default_credentials = default_session.get_credentials()

        self.bucket_name = bucket
        self.access_key = \
            access_key or getattr(default_credentials, 'access_key', None)
        self.secret_key = \
            secret_key or getattr(default_credentials, 'secret_key', None)
        self.region_name = \
            region_name or default_session.get_config_variable('region')
        self.file_acl = 'public-read'
        self.s3 = boto3.resource(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        )
        self._verify_configuration()

    @property
    def base_url(self):
        """The base URL for the storage's bucket

        Returns:
            str: The URL
        """
        return '/'.join([self.s3.meta.client._endpoint.host, self.bucket_name])

    def _verify_configuration(self):
        if self.access_key is None:
            raise exc.InvalidResizeSettingError(
                "Could not find S3 setting for access_key"
            )
        if self.secret_key is None:
            raise exc.InvalidResizeSettingError(
                "Could not find S3 setting for secret_key"
            )
        if self.region_name is None:
            raise exc.InvalidResizeSettingError(
                "Could not find S3 setting for region_name"
            )

    def get(self, relative_path):
        """Get binary file data for specified key

        Args:
            key (str): The key to get data for

        Returns:
            bytes: The file's binary data
        """
        if not relative_path:
            raise exc.ImageNotFoundError()
        obj = self.s3.Object(self.bucket_name, relative_path)
        try:
            resp = obj.get()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                new_exc = exc.ImageNotFoundError(*e.args)
                new_exc.original_exc = e
                raise new_exc
            else:
                raise
        return resp['Body'].read()

    def save(self, relative_path, bdata):
        """Store binary file data at specified key

        Args:
            key (str): The key to store data at
            bdata (bytes): The file data
        """
        self.s3.meta.client.put_object(
            Bucket=self.bucket_name,
            Key=relative_path,
            Body=bdata,
            ACL=self.file_acl
        )

    def exists(self, relative_path):
        """Check if the key exists in the backend

        Args:
            key (str): The key to check

        Returns:
            bool: Whether the key exists or not
        """
        if not relative_path:
            return False
        try:
            self.s3.meta.client.head_object(
                Bucket=self.bucket_name,
                Key=relative_path
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise
        else:
            return True

    def delete(self, relative_path):
        """Delete file at specified key

        Args:
            key (str): The key to delete
        """
        return self.s3.meta.client.delete_object(
            Bucket=self.bucket_name,
            Key=relative_path,
        )

    def list_tree(self, subdir):
        """
        Recursively yields all keys in a sub-directory of the storage backend

        Args:
            subdir (str):
                The subdirectory to list keys for

        Returns:
            Generator[str, str, None]:
                Yields subdirectory's keys
        """
        assert subdir, 'Subdir must be specified'
        if not subdir.endswith('/'):
            subdir += '/'

        kw = dict(Bucket=self.bucket_name, Prefix=subdir)

        while True:
            resp = self.s3.meta.client.list_objects_v2(**kw)
            for obj in resp.get('Contents', ()):
                yield obj['Key']
            if resp.get('NextContinuationToken'):
                kw['ContinuationToken'] = resp['NextContinuationToken']
            else:
                break

    def delete_tree(self, subdir):
        """
        Recursively deletes all keys in specified sub-directory (prefix)

        Args:
            subdir (str):
                The subdirectory to delete keys in

        Returns:
            Generator[str, str, None]:
                Yields subdirectory's deleted keys
        """
        assert subdir, 'Subdir must be specified'

        for keys in utils.chunked(self.list_tree(subdir), 1000):
            self.s3.meta.client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    'Objects': [{'Key': key} for key in keys]
                }
            )
            for key in keys:
                yield key
