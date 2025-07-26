from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from PIL import Image
from io import BytesIO
import tempfile

# ImageKit config
imagekit = ImageKit(
    public_key='***REMOVED***',
    private_key='***REMOVED***',
    url_endpoint='https://ik.imagekit.io/linkup'
)

# Convert to webp
input_path = "test/test.jpg"
img = Image.open(input_path).convert("RGB")
buffer = BytesIO()
img.save(buffer, format="WEBP", quality=80, method=6)
buffer.seek(0)

# Save to temp file (reliable for ImageKit SDK)
with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as tmp:
    tmp.write(buffer.read())
    tmp_path = tmp.name

# Upload from temp file
options = UploadFileRequestOptions(folder="/test", is_private_file=False)
with open(tmp_path, "rb") as f:
    upload = imagekit.upload(file=f, file_name="converted_test.webp", options=options)

print(f"[RESULT] URL: {upload.url}")
