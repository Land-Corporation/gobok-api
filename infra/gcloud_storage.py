from django.conf import settings
from google.cloud import storage


class GCloudStorage:
    """Provides access to GCS for uploading/downloading static assets."""

    def __init__(self, bucket_name=getattr(settings, 'GCS_BUCKET_NAME', None)):
        self._map_image = None
        storage_client = storage.Client()
        self.bucket = storage_client.bucket(bucket_name)

    def upload_image_from_bytes(self, image_file_name: str, image_file: bytes):
        # save like 'v1.0/image_file_name'
        file_dir = f'images/{image_file_name}'
        blob = self.bucket.blob(file_dir)
        return blob.upload_from_string(image_file, content_type='image/png')

    def delete_image_file(self, image_file_name: str, image: str):
        blob = self.bucket.blob(image_file_name)
        blob.delete(data=image)

    def download_map_image(self, location_id: str, image_file_name: str):
        file_dir = f'{location_id}/{image_file_name}'
        blob = self.bucket.blob(file_dir)
        return blob.download_as_bytes()
