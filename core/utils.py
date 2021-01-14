import io

from PIL import Image, ImageOps
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile


def process_image_data_from_request(request) -> bytes:
    mem_file: InMemoryUploadedFile = request.FILES.get('file', None)
    if not mem_file:
        raise FileNotFoundError('File not found in the request')
    mem_file.file.seek(0)  # reset stream to initial position
    return mem_file.file.read()


def convert_image_to_thumbnail(original_image: bytes) -> bytes:
    image = Image.open(io.BytesIO(original_image))
    image = ImageOps.fit(image, settings.THUMBNAIL_DIMENSION, Image.ANTIALIAS)
    buf = io.BytesIO()
    image.save(buf, format='PNG', quality=100)
    return buf.getvalue()
