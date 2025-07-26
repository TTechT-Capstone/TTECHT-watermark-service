# routes/image_routes.py
from flask import Blueprint
from controller.image_controller import ImageController

# Create blueprint
image_bp = Blueprint('image', __name__, url_prefix='/api/images')

# Initialize controller
image_controller = ImageController()

# Define routes
@image_bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload base64 image endpoint"""
    return image_controller.upload_image()

@image_bp.route('/<path:public_id>/info', methods=['GET'])
def get_image_info(public_id):
    """Get image info by public ID endpoint"""
    return image_controller.get_image_info(public_id)

@image_bp.route('/<path:public_id>', methods=['DELETE'])
def delete_image(public_id):
    """Delete image endpoint"""
    return image_controller.delete_image(public_id)

@image_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return image_controller.health_check()

# Error handlers for the blueprint
@image_bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle request too large error"""
    return {
        'error': 'Request entity too large',
        'code': 'REQUEST_TOO_LARGE'
    }, 413

@image_bp.errorhandler(415)
def unsupported_media_type(error):
    """Handle unsupported media type error"""
    return {
        'error': 'Unsupported media type',
        'code': 'UNSUPPORTED_MEDIA_TYPE'
    }, 415