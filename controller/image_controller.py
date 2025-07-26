# controller/image_controller.py
from flask import request, jsonify
from service.image_service import ImageService

class ImageController:
    def __init__(self):
        self.image_service = ImageService()

    def upload_image(self):
        """
        Handle image upload request
        
        Expected JSON payload:
        {
            "image": "base64_encoded_string_here"
        }
        
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Validate request content type
            if not request.is_json:
                return jsonify({
                    'error': 'Content-Type must be application/json',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400

            # Get request data
            data = request.get_json()
            
            # Validate payload structure
            validation_error = self._validate_upload_payload(data)
            if validation_error:
                return validation_error

            # Process upload through service
            result = self.image_service.upload_base64_image(data['image'])
            
            return jsonify({
                'success': True,
                'message': 'Image uploaded successfully',
                'data': result
            }), 201

        except ValueError as e:
            return jsonify({
                'error': str(e),
                'code': 'VALIDATION_ERROR'
            }), 400

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'UPLOAD_ERROR'
            }), 500

    def get_image_info(self, public_id):
        """
        Handle get image info request
        
        Args:
            public_id: Cloudinary public ID from URL parameter
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            if not public_id:
                return jsonify({
                    'error': 'Public ID is required',
                    'code': 'INVALID_ID'
                }), 400

            # Get image info through service
            result = self.image_service.get_image_info(public_id)
            
            return jsonify({
                'success': True,
                'data': result
            }), 200

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'RETRIEVAL_ERROR'
            }), 500

    def delete_image(self, public_id):
        """
        Handle delete image request
        
        Args:
            public_id: Cloudinary public ID from URL parameter
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            if not public_id:
                return jsonify({
                    'error': 'Public ID is required',
                    'code': 'INVALID_ID'
                }), 400

            # Delete image through service
            success = self.image_service.delete_image(public_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Image deleted successfully'
                }), 200
            else:
                return jsonify({
                    'error': 'Failed to delete image',
                    'code': 'DELETE_FAILED'
                }), 500

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'DELETE_ERROR'
            }), 500

    def health_check(self):
        """Handle health check request"""
        return jsonify({
            'status': 'healthy',
            'service': 'image_service',
            'version': '1.0.0'
        }), 200

    def _validate_upload_payload(self, data):
        """
        Validate upload request payload
        
        Args:
            data: Request JSON data
            
        Returns:
            tuple or None: Error response tuple if validation fails, None if valid
        """
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'MISSING_BODY'
            }), 400

        if 'image' not in data:
            return jsonify({
                'error': 'Missing required field: image',
                'code': 'MISSING_FIELD'
            }), 400

        if not data['image'] or not isinstance(data['image'], str):
            return jsonify({
                'error': 'Image must be a non-empty base64 string',
                'code': 'INVALID_IMAGE_DATA'
            }), 400

        return None