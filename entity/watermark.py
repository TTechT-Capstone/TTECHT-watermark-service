from db import db

class Watermark(db.Model):
    __tablename__ = 'watermark'

    watermark_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    watermark_url_image = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "watermark_id": self.watermark_id,
            "store_name": self.store_name,
            "watermark_url_image": self.watermark_url_image
        }
