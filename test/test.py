import face_recognition
from PIL import Image

def extract_face(image_path, save_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)

    if not face_locations:
        print("No face detected.")
        return False

    # Use the first detected face
    top, right, bottom, left = face_locations[0]
    face_image = image[top:bottom, left:right]
    pil_image = Image.fromarray(face_image)
    pil_image.save(save_path)
    return True

# Usage
extract_face("test/face.webp", "test/user123.jpg")
