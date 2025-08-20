# routes/image_routes.py
from flask import Blueprint
from controller.image_controller import ImageController

# Create blueprint
image_bp = Blueprint("image", __name__, url_prefix="/api/images")
image_bp.strict_slashes = False  # accept /path and /path/

# Initialize controller
image_controller = ImageController()

# Simple index so browser GET works
@image_bp.get("/")
def index():
    return {
        "ok": True,
        "service": "TTECHT-watermark-service",
        "endpoints": [
            "POST /api/images/upload",
            "POST /api/images/embed-watermark",
            "POST /api/images/extract-watermark",
            "POST /api/images/detect-watermark",
            "GET  /api/images/<public_id>/info",
            "DELETE /api/images/<public_id>",
            "GET  /api/images/health"
        ]
    }, 200

# Define routes
@image_bp.post("/upload")
def upload_image():
    """Upload base64 image endpoint"""
    return image_controller.upload_image()

@image_bp.get("/<path:public_id>/info")
def get_image_info(public_id):
    """Get image info by public ID endpoint"""
    return image_controller.get_image_info(public_id)

@image_bp.delete("/<path:public_id>")
def delete_image(public_id):
    """Delete image endpoint"""
    return image_controller.delete_image(public_id)

@image_bp.post("/embed-watermark")
def embed_watermark():
    """Embed watermark into image endpoint"""
    return image_controller.embed_watermark()

@image_bp.post("/extract-watermark")
def extract_watermark():
    """Extract watermark from suspect image endpoint"""
    return image_controller.extract_watermark()

@image_bp.post("/detect-watermark")
def detect_watermark():
    """Detect/compare watermarks using statistical metrics endpoint"""
    return image_controller.detect_watermark()

@image_bp.get("/health")
def health_check():
    """Health check endpoint"""
    return image_controller.health_check()

# Error handlers for the blueprint
@image_bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle request too large error"""
    return {"error": "Request entity too large", "code": "REQUEST_TOO_LARGE"}, 413

@image_bp.errorhandler(415)
def unsupported_media_type(error):
    """Handle unsupported media type error"""
    return {"error": "Unsupported media type", "code": "UNSUPPORTED_MEDIA_TYPE"}, 415
