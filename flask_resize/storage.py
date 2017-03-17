import os

from . import exc, utils
from ._compat import PY2, boto3, botocore


class Storage:

    def __init__(self, *args, **kwargs):
        pass

    def get(self, relative_path):
        raise NotImplementedError

    def save(self, relative_path, bdata):
        raise NotImplementedError

    def delete(self, relative_path):
        raise NotImplementedError

    def exists(self, relative_path):
        raise NotImplementedError


class FileStorage(Storage):

    def __init__(self, base_path):
        self.base_path = base_path

    def _get_full_path(self, relative_path):
        return os.path.join(self.base_path, relative_path)

    def get(self, relative_path):
        if not relative_path:
            raise exc.ImageNotFoundError()
        path = self._get_full_path(relative_path)
        try:
            with open(path, 'rb') as fp:
                return fp.read()
        except IOError as e:
            if e.errno == 2:
                raise exc.ImageNotFoundError(*e.args)
            else:
                raise

    def save(self, relative_path, bdata):
        full_path = self._get_full_path(relative_path)
        utils.mkdir_p(full_path.rpartition('/')[0])

        # Python 2 doesn't natively support `xb` mode as used below. Have to
        # manually check for the file's existence.
        if PY2 and self.exists(relative_path):
            raise exc.FileExistsError(17, 'File exists')
        with open(full_path, 'wb' if PY2 else 'xb') as fp:
            fp.write(bdata)

    def delete(self, relative_path):
        os.remove(self._get_full_path(relative_path))

    def exists(self, relative_path):
        if not relative_path:
            return False
        full_path = self._get_full_path(relative_path)
        return os.path.exists(full_path)


class S3Storage(Storage):

    def __init__(
        self,
        bucket,
        access_key=None,
        secret_key=None,
        region_name=None
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
        self.s3 = boto3.resource(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        )
        self.bucket = self.s3.Bucket(self.bucket_name)
        self._verify_configuration()

    @property
    def base_url(self):
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
        self.bucket.put_object(
            Key=relative_path,
            Body=bdata,
            ACL='public-read'
        )

    def delete(self, relative_path):
        return self.s3.Object(self.bucket_name, relative_path).delete()

    def exists(self, relative_path):
        if not relative_path:
            return False
        try:
            self.s3.Object(self.bucket_name, relative_path).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise
        else:
            return True
