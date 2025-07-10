from entity.watermark import Watermark
from db import db

class WatermarkRepository:
    @staticmethod
    def get_all():
        return Watermark.query.all()

    @staticmethod
    def get_by_id(watermark_id):
        return Watermark.query.get(watermark_id)

    @staticmethod
    def add(watermark):
        db.session.add(watermark)
        db.session.commit()
        return watermark
