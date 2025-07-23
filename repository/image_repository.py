from entity.image import Image
from db import db

class ImageRepository:
    @staticmethod
    def save(image: Image) -> Image:
        db.session.add(image)
        db.session.commit()
        return image

    @staticmethod
    def get_by_public_id(public_id: str) -> Image:
        return Image.query.filter_by(public_id=public_id).first()
