from django.core.files.uploadedfile import InMemoryUploadedFile



def process_image_data_from_request(request) -> bytes:
    mem_file: InMemoryUploadedFile = request.FILES.get('file', None)
    if not mem_file:
        raise FileNotFoundError('File not found in the request')
    mem_file.file.seek(0)  # reset stream to initial position
    return mem_file.file.read()
