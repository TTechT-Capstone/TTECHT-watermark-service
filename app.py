# app.py
import os
from flask import Flask, jsonify
from dotenv import load_dotenv

# Try Cloudinary, but don't require it - only to test on local storage
try:
    import cloudinary
    CLOUDINARY_OK = True
except Exception:
    CLOUDINARY_OK = False

# Load environment variables from .env if present
load_dotenv()


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # ---- Flask config ----
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
    app.config['JSON_SORT_KEYS'] = False

    # ---- Optional Cloudinary config ----
    if CLOUDINARY_OK and os.getenv('CLOUDINARY_CLOUD_NAME'):
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )
    else:
        # Safe fallback; service will use local storage
        app.logger.info("Cloudinary not configured. Using local storage.")

    # ---- Register routes/blueprints ----
    # Import here to avoid circular imports
    from routes.image_routes import image_bp
    app.register_blueprint(image_bp)

    # ---- Global error handlers ----
    @app.errorhandler(404)
    def not_found(_):
        return {'error': 'Endpoint not found', 'code': 'NOT_FOUND'}, 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return {'error': 'Method not allowed', 'code': 'METHOD_NOT_ALLOWED'}, 405

    @app.errorhandler(500)
    def internal_error(_):
        return {'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}, 500

    # ---- Friendly browser routes ----
    @app.get("/")
    def index():
        return jsonify({
            "ok": True,
            "service": "TTechT Watermark Service API",
            "try": ["GET /health", "POST /api/images/extract-watermark", "POST /api/images/detect-watermark"]
        }), 200

    @app.get("/health")
    def health():
        return {'status': 'healthy'}, 200

    return app


# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Match your previous port; change as you like
    app.run(debug=True, host='0.0.0.0', port=8000)
