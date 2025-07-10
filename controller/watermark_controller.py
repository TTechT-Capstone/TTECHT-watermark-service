from flask import Blueprint, jsonify, request
from service.watermark_service import WatermarkService

watermark_bp = Blueprint('watermark_bp', __name__)

@watermark_bp.route('/watermarks', methods=['GET'])
def get_watermarks():
    watermarks = WatermarkService.get_all_watermarks()
    return jsonify([w.to_dict() for w in watermarks])

@watermark_bp.route('/watermarks/<int:watermark_id>', methods=['GET'])
def get_watermark(watermark_id):
    watermark = WatermarkService.get_watermark_by_id(watermark_id)
    if not watermark:
        return jsonify({"error": "Watermark not found"}), 404
    return jsonify(watermark.to_dict())

@watermark_bp.route('/watermarks', methods=['POST'])
def create_watermark():
    data = request.json
    store_name = data.get('store_name')
    watermark_url_image = data.get('watermark_url_image')
    watermark = WatermarkService.create_watermark(store_name, watermark_url_image)
    return jsonify(watermark.to_dict()), 201
