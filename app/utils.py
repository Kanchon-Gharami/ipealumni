from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def compress_image(image, max_size=500):
    img = Image.open(image)

    # Initial reduction
    img.thumbnail((1000, 1000))

    # Fine-tuning
    quality = 90  # initial quality
    while True:
        temp_buffer = BytesIO()
        img.save(temp_buffer, format='JPEG', quality=quality)
        temp_buffer.seek(0)
        if len(temp_buffer.read()) <= max_size * 1024:
            break
        quality -= 10
        if quality <= 10:  # Don't reduce quality below 10
            break

    img.save(image.path, format='JPEG', quality=quality)

