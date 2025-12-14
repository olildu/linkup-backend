import blurhash
import io
from PIL import Image

from app.controllers.b2_controller import bucket


def generate_signed_url(file_key: str, valid_duration: int = 3600) -> str:
    authorization_token = bucket.get_download_authorization(
        file_name_prefix=file_key,
        valid_duration_in_seconds=valid_duration
    )
    
    base_url = bucket.get_download_url(file_key)
    return f"{base_url}?Authorization={authorization_token}"

def generate_blurhash(image_data: bytes) -> str:
    with Image.open(io.BytesIO(image_data)) as image_file:
        image_file.thumbnail(( 100, 100 ))
        hash = blurhash.encode(image_file, x_components=9, y_components=9)  
        return hash