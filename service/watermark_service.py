from repository.watermark_repository import WatermarkRepository
from entity.watermark import Watermark

class WatermarkService:
    @staticmethod
    def get_all_watermarks():
        return WatermarkRepository.get_all()

    @staticmethod
    def get_watermark_by_id(watermark_id):
        return WatermarkRepository.get_by_id(watermark_id)

    @staticmethod
    def create_watermark(store_name, watermark_url_image):
        watermark = Watermark(store_name=store_name, watermark_url_image=watermark_url_image)
        return WatermarkRepository.add(watermark)
