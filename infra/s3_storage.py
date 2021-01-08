from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class S3DefaultFileStorage(S3Boto3Storage):
    location = settings.AWS_STORAGE_FILE_LOCATION
    default_acl = 'private'  # private access using signature
    file_overwrite = False


class S3MediaStorage(S3Boto3Storage):
    location = settings.AWS_STORAGE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False


class S3ImageStorage(S3Boto3Storage):
    location = settings.AWS_STORAGE_IMAGE_LOCATION
    default_acl = 'private'
    file_overwrite = False
