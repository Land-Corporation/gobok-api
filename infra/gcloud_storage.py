from django.conf import settings
from google.cloud import storage


class GCloudStorage:
    """Provides access to GCS for uploading/downloading static assets."""

    PUBLIC_URI_PREFIX = 'https://storage.googleapis.com'

    def __init__(self, bucket_name=getattr(settings, 'GCS_BUCKET_NAME', None)):
        storage_client = storage.Client()
        self.bucket = storage_client.bucket(bucket_name)

    # Image handlers
    def upload_image_from_bytes(self, image_file_name: str, image_file: bytes,
                                make_public: bool = False):
        # setup file
        file_dir = f'{settings.GCS_IMAGE_FOLDER_NAME}/{image_file_name}'
        blob = self.bucket.blob(file_dir)

        # upload to GCS
        blob.upload_from_string(image_file)

        # make publicly accessible
        if make_public:
            blob.make_public()

    def delete_image_file(self, image_file_name: str, image: str):
        blob = self.bucket.blob(image_file_name)
        blob.delete(data=image)

    def download_image_file(self, location_id: str, image_file_name: str):
        file_dir = f'{location_id}/{image_file_name}'
        blob = self.bucket.blob(file_dir)
        return blob.download_as_bytes()

    def get_image_public_access_url(self, image_filename: str) -> str:
        return f'{self.PUBLIC_URI_PREFIX}/{settings.GCS_BUCKET_NAME}/{settings.GCS_IMAGE_FOLDER_NAME}/{image_filename}'
