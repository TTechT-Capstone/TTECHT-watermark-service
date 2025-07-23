import os
from flask import Blueprint, request, jsonify
from service.image_service import ImageService
from repository.image_repository import ImageRepository

image_bp = Blueprint('image', __name__, url_prefix='/api')

# instantiate service with its repository
image_service = ImageService(ImageRepository())

ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'gif'}
def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

@image_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'No selected file or unsupported type'}), 400

    try:
        folder = os.getenv('CLOUDINARY_UPLOAD_FOLDER', 'watermark_app/')
        transformation = [{'width': 1024, 'crop': 'limit'}]

        img = image_service.upload(
            file.stream,
            folder=folder,
            transformation=transformation
        )

        return jsonify({
            'id':         img.id,
            'public_id':  img.public_id,
            'url':        img.url,
            'width':      img.width,
            'height':     img.height,
            'format':     img.format,
            'created_at': img.created_at.isoformat()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
