# routes/watermark_routes.py
from flask import Blueprint
from controller.watermark_controller import WatermarkController

# Create blueprint
watermark_bp = Blueprint('watermark', __name__, url_prefix='/api/watermarks')

# Initialize controller
watermark_controller = WatermarkController()

# Define watermark CRUD routes
@watermark_bp.route('/', methods=['POST'])
def create_watermark():
    """Create a new watermark endpoint"""
    return watermark_controller.create_watermark()

@watermark_bp.route('/', methods=['GET'])
def get_all_watermarks():
    """Get all watermarks endpoint"""
    return watermark_controller.get_all_watermarks()

@watermark_bp.route('/search', methods=['GET'])
def search_watermarks():
    """Search watermarks by store name endpoint"""
    return watermark_controller.search_watermarks()

@watermark_bp.route('/<int:watermark_id>', methods=['GET'])
def get_watermark(watermark_id):
    """Get watermark by ID endpoint"""
    return watermark_controller.get_watermark(watermark_id)

@watermark_bp.route('/<int:watermark_id>', methods=['PUT'])
def update_watermark(watermark_id):
    """Update watermark by ID endpoint"""
    return watermark_controller.update_watermark(watermark_id)

@watermark_bp.route('/<int:watermark_id>', methods=['DELETE'])
def delete_watermark(watermark_id):
    """Delete watermark by ID endpoint"""
    return watermark_controller.delete_watermark(watermark_id)

# Error handlers for the watermark blueprint
@watermark_bp.errorhandler(404)
def watermark_not_found(error):
    """Handle watermark not found error"""
    return {
        'error': 'Watermark endpoint not found',
        'code': 'WATERMARK_ENDPOINT_NOT_FOUND'
    }, 404

@watermark_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed error"""
    return {
        'error': 'Method not allowed for watermark endpoint',
        'code': 'WATERMARK_METHOD_NOT_ALLOWED'
    }, 405
