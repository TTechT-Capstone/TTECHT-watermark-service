import cloudinary.uploader
from entity.image import Image
from repository.image_repository import ImageRepository

class ImageService:
    def __init__(self, repo: ImageRepository):
        self.repo = repo

    def upload(self, file_stream, folder: str, transformation: list = None) -> Image:
        upload_params = {'folder': folder}
        if transformation:
            upload_params['transformation'] = transformation

        result = cloudinary.uploader.upload(file_stream, **upload_params)

        img = Image(
            public_id=result['public_id'],
            url=result['secure_url'],
            width=result.get('width'),
            height=result.get('height'),
            format=result.get('format')
        )
        return self.repo.save(img)
