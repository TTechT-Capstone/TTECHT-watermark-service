import os
from flask import Flask
from dotenv import load_dotenv
import cloudinary

from db import db
from controller.watermark_controller import watermark_bp
from controller.image_controller import image_bp
    
# 1. load .env
load_dotenv()

# 2. flask + db setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql+psycopg2://user:12345@localhost:5432/watermark_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. cloudinary config
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key    = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET'),
    secure     = True
)

# 4. register extensions & blueprints
db.init_app(app)
app.register_blueprint(watermark_bp)
app.register_blueprint(image_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
