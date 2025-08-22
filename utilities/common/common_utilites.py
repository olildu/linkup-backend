from controllers.imagekit_controller import imagekit

def get_signed_imagekit(image_metadata : dict, expire_seconds : int = 7200):
    image_metadata['url'] = imagekit.url({
        "path": image_metadata['file_key'],
        "signed": True,
        "expire_seconds": expire_seconds
    })
    print(image_metadata)
    return image_metadata