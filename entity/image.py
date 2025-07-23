from datetime import datetime
from db import db

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(255), nullable=False, unique=True)
    url = db.Column(db.String(512), nullable=False)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    format = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
