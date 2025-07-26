import asyncio
import tempfile
import face_recognition
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, BackgroundTasks
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from enum import Enum
import uuid
from io import BytesIO
from PIL import Image
import time

from constants.global_constants import oauth2_scheme
from utilities.media.media_utilities import generate_blurhash
from utilities.token.token_utilities import decode_token
from controllers.b2_controller import bucket
from controllers.imagekit_controller import imagekit
from controllers.logger_controller import logger_controller

common_router = APIRouter(prefix="/upload")

class MediaTypeEnum(str, Enum):
    IMAGE = "image"
    VOICE = "voice"

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 5 MB

async def upload_file_async_chat(webp_content: bytes, file_key: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, bucket.upload_bytes, webp_content, file_key)

async def upload_file_async_user(file_path: str, file_key: str) -> tuple[str, str]:
    parts = file_key.split("/")
    folder = f"/{parts[0]}/{parts[1]}"
    file_name = parts[-1]
    options = UploadFileRequestOptions(folder=folder, is_private_file=True)

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: imagekit.upload(
        file=open(file_path, "rb"), file_name=file_name, options=options
    ))

    return result.url, imagekit.url({
        "path": f"{folder}/{file_name}",
        "signed": True,
        "expire_seconds": 1200
    })

def process_image_half_and_convert_webp(content: bytes) -> tuple[bytes, int, int]:
    image = Image.open(BytesIO(content))
    original_width, original_height = image.size
    width, height = original_width // 2, original_height // 2
    image = image.resize((width, height), Image.Resampling.LANCZOS)

    webp_buffer = BytesIO()
    image.save(webp_buffer, format="WEBP", quality=75)
    return webp_buffer.getvalue(), width, height

def process_image_to_webp_file(content: bytes) -> tuple[str, bytes, int, int]:
    image = Image.open(BytesIO(content))
    original_width, original_height = image.size
    width, height = original_width // 2, original_height // 2
    image = image.resize((width, height), Image.Resampling.LANCZOS)

    with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as temp_file:
        image.save(temp_file, format="WEBP", quality=75)
        temp_file_path = temp_file.name

    with open(temp_file_path, "rb") as f:
        webp_content = f.read()

    return temp_file_path, webp_content, width, height

def extract_face(image_path, save_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)

    if not face_locations:
        print("No face detected.")
        return False

    top, right, bottom, left = face_locations[0]
    face_image = image[top:bottom, left:right]
    pil_image = Image.fromarray(face_image)
    pil_image.save(save_path)
    return True


@common_router.post("/media")
async def upload_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    media_type: MediaTypeEnum = Form(...),
    token: str = Depends(oauth2_scheme),
):
    try:
        user_id = decode_token(token)
        content = await file.read()

        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB")

        loop = asyncio.get_event_loop()
        webp_content, width, height = await loop.run_in_executor(None, process_image_half_and_convert_webp, content)

        if len(webp_content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="Converted file too large.")

        file_key = f"media/{user_id}/{uuid.uuid4()}.webp"
        blurhash = generate_blurhash(webp_content)

        start_time = time.time()
        await upload_file_async_chat(webp_content, file_key)
        logger_controller.info(f"Upload time for {file_key}: {time.time() - start_time:.2f} sec")

        auth_token = bucket.get_download_authorization(file_name_prefix=file_key, valid_duration_in_seconds=600)
        base_url = bucket.get_download_url(file_key)
        signed_url = f"{base_url}?Authorization={auth_token}"

        return {
            "file_key": file_key,
            "media_type": media_type,
            "metadata": {
                "file_url": signed_url,
                "width": float(width),
                "height": float(height),
                "blurhash": blurhash,
                "format": "webp",
                "size_bytes": len(webp_content),
            },
        }

    except HTTPException as e:
        logger_controller.warning(f"Exception in uploading file {e}")
        raise
    except Exception as e:
        logger_controller.warning(f"Exception in uploading file {e}")
        raise HTTPException(status_code=500, detail=str(e))

@common_router.post("/media-user")
async def upload_media_user(
    file: UploadFile = File(...),
    media_type: MediaTypeEnum = Form(...),
    token: str = Depends(oauth2_scheme),
):
    try:
        user_id = decode_token(token)
        content = await file.read()
        try:
            Image.open(BytesIO(content)).verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file.")
        
        loop = asyncio.get_event_loop()
        temp_file_path, webp_content, width, height = await loop.run_in_executor(None, process_image_to_webp_file, content)

        if len(webp_content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="Converted file too large.")

        blurhash = generate_blurhash(webp_content)

        file_key = f"media/{user_id}/{uuid.uuid4()}.webp"
        start_time = time.time()
        file_url, signed_url = await upload_file_async_user(temp_file_path, file_key)
        logger_controller.info(f"Upload time for {file_key}: {time.time() - start_time:.2f}s")

        return {
            "file_key": file_key,
            "media_type": media_type,
            "metadata": {
                "file_url": file_url,
                "signed_url": signed_url,
                "width": float(width),
                "height": float(height),
                "blurhash": blurhash,
                "format": "webp",
                "size_bytes": len(webp_content),
            },
        }

    except HTTPException as e:
        logger_controller.warning(f"Upload error: {e}")
        raise
    except Exception as e:
        logger_controller.warning(f"Unhandled upload error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong during upload.")

@common_router.post("/media-user-pfp")
async def generate_profile_picture(
    file: UploadFile = File(...),
    media_type: MediaTypeEnum = Form(...),
    token: str = Depends(oauth2_scheme),
):
    try:
        user_id = decode_token(token)
        content = await file.read()

        # Validate image
        try:
            Image.open(BytesIO(content)).verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file.")

        # Save original image to temp file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_input_file:
            temp_input_file.write(content)
            input_path = temp_input_file.name

        # Upload original image to imagekit
        original_file_key = f"media/{user_id}/{uuid.uuid4()}.jpg"
        _, original_signed_url = await upload_file_async_user(input_path, original_file_key)

        # Temp file for cropped face
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_face_file:
            face_path = temp_face_file.name

        if not extract_face(input_path, face_path):
            raise HTTPException(status_code=422, detail="No face detected in the image.")

        # Read cropped face image bytes
        with open(face_path, "rb") as f:
            face_bytes = f.read()

        # Convert face image to webp
        loop = asyncio.get_event_loop()
        temp_file_path, webp_content, width, height = await loop.run_in_executor(
            None, process_image_to_webp_file, face_bytes
        )

        if len(webp_content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="Converted file too large.")

        # Upload profile picture (webp)
        profile_file_key = f"profile_pictures/{user_id}/pfp.webp"
        blurhash = generate_blurhash(webp_content)

        start_time = time.time()
        profile_url, profile_signed_url = await upload_file_async_user(temp_file_path, profile_file_key)
        logger_controller.info(f"PFP Upload time for {profile_file_key}: {time.time() - start_time:.2f}s")

        return {
            "original_file_key": original_file_key,
            "profile_file_key": profile_file_key,
            "media_type": media_type,
            "original_image_url": original_signed_url,
            "profile_picture_url": profile_signed_url,
            "metadata": {
                "width": float(width),
                "height": float(height),
                "blurhash": blurhash,
                "format": "webp",
                "size_bytes": len(webp_content),
            },
        }

    except HTTPException as e:
        logger_controller.warning(f"PFP Upload error: {e}")
        raise
    except Exception as e:
        logger_controller.warning(f"Unhandled PFP upload error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong during profile picture upload.")
