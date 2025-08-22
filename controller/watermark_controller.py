# controller/watermark_controller.py
from flask import request, jsonify
from service.watermark_service import WatermarkService

class WatermarkController:
    def __init__(self):
        self.watermark_service = WatermarkService()

    def create_watermark(self):
        """
        Handle watermark creation request
        
        Expected JSON payload:
        {
            "store_name": "Store Name",
            "watermark_url_image": "URL or path to watermark image"
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
            validation_error = self._validate_create_watermark_payload(data)
            if validation_error:
                return validation_error

            # Extract parameters
            store_name = data['store_name']
            watermark_url_image = data['watermark_url_image']

            # Process watermark creation through service
            watermark = self.watermark_service.create_watermark(
                store_name=store_name,
                watermark_url_image=watermark_url_image
            )
            
            return jsonify({
                'success': True,
                'message': 'Watermark created successfully',
                'data': watermark.to_dict()
            }), 201

        except ValueError as e:
            return jsonify({
                'error': str(e),
                'code': 'VALIDATION_ERROR'
            }), 400

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'WATERMARK_CREATE_ERROR'
            }), 500

    def get_watermark(self, watermark_id: int):
        """
        Handle get watermark by ID request
        
        Args:
            watermark_id: ID of the watermark to retrieve
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Get watermark through service
            watermark = self.watermark_service.get_watermark_by_id(watermark_id)
            
            if watermark:
                return jsonify({
                    'success': True,
                    'data': watermark.to_dict()
                }), 200
            else:
                return jsonify({
                    'error': f'Watermark with ID {watermark_id} not found',
                    'code': 'WATERMARK_NOT_FOUND'
                }), 404

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'WATERMARK_RETRIEVAL_ERROR'
            }), 500

    def get_all_watermarks(self):
        """
        Handle get all watermarks request
        
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Get all watermarks through service
            watermarks = self.watermark_service.get_all_watermarks()
            
            return jsonify({
                'success': True,
                'data': {
                    'watermarks': [w.to_dict() for w in watermarks],
                    'count': len(watermarks)
                }
            }), 200

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'WATERMARK_RETRIEVAL_ERROR'
            }), 500

    def update_watermark(self, watermark_id: int):
        """
        Handle watermark update request
        
        Expected JSON payload:
        {
            "store_name": "New Store Name",  // optional
            "watermark_url_image": "New URL or path"  // optional
        }
        
        Args:
            watermark_id: ID of the watermark to update
            
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
            validation_error = self._validate_update_watermark_payload(data)
            if validation_error:
                return validation_error

            # Extract parameters
            store_name = data.get('store_name')
            watermark_url_image = data.get('watermark_url_image')

            # Process watermark update through service
            watermark = self.watermark_service.update_watermark(
                watermark_id=watermark_id,
                store_name=store_name,
                watermark_url_image=watermark_url_image
            )
            
            if watermark:
                return jsonify({
                    'success': True,
                    'message': 'Watermark updated successfully',
                    'data': watermark.to_dict()
                }), 200
            else:
                return jsonify({
                    'error': f'Watermark with ID {watermark_id} not found',
                    'code': 'WATERMARK_NOT_FOUND'
                }), 404

        except ValueError as e:
            return jsonify({
                'error': str(e),
                'code': 'VALIDATION_ERROR'
            }), 400

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'WATERMARK_UPDATE_ERROR'
            }), 500

    def delete_watermark(self, watermark_id: int):
        """
        Handle watermark deletion request
        
        Args:
            watermark_id: ID of the watermark to delete
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Delete watermark through service
            success = self.watermark_service.delete_watermark(watermark_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Watermark with ID {watermark_id} deleted successfully'
                }), 200
            else:
                return jsonify({
                    'error': f'Watermark with ID {watermark_id} not found',
                    'code': 'WATERMARK_NOT_FOUND'
                }), 404

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'WATERMARK_DELETE_ERROR'
            }), 500

    def search_watermarks(self):
        """
        Handle watermark search request
        
        Query parameter: q (search query)
        
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Get search query from query parameters
            query = request.args.get('q', '')
            
            if not query:
                return jsonify({
                    'error': 'Search query parameter "q" is required',
                    'code': 'MISSING_QUERY'
                }), 400

            # Search watermarks through service
            watermarks = self.watermark_service.search_watermarks(query)
            
            return jsonify({
                'success': True,
                'data': {
                    'query': query,
                    'watermarks': [w.to_dict() for w in watermarks],
                    'count': len(watermarks)
                }
            }), 200

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'WATERMARK_SEARCH_ERROR'
            }), 500

    def _validate_create_watermark_payload(self, data):
        """
        Validate watermark creation request payload
        
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

        if 'store_name' not in data:
            return jsonify({
                'error': 'Missing required field: store_name',
                'code': 'MISSING_FIELD'
            }), 400

        if 'watermark_url_image' not in data:
            return jsonify({
                'error': 'Missing required field: watermark_url_image',
                'code': 'MISSING_FIELD'
            }), 400

        if not data['store_name'] or not isinstance(data['store_name'], str):
            return jsonify({
                'error': 'store_name must be a non-empty string',
                'code': 'INVALID_STORE_NAME'
            }), 400

        if not data['watermark_url_image'] or not isinstance(data['watermark_url_image'], str):
            return jsonify({
                'error': 'watermark_url_image must be a non-empty string',
                'code': 'INVALID_IMAGE_URL'
            }), 400

        return None

    def _validate_update_watermark_payload(self, data):
        """
        Validate watermark update request payload
        
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

        # At least one field must be provided
        if 'store_name' not in data and 'watermark_url_image' not in data:
            return jsonify({
                'error': 'At least one field (store_name or watermark_url_image) must be provided',
                'code': 'MISSING_FIELDS'
            }), 400

        # Validate store_name if provided
        if 'store_name' in data and data['store_name'] is not None:
            if not isinstance(data['store_name'], str) or not data['store_name'].strip():
                return jsonify({
                    'error': 'store_name must be a non-empty string',
                    'code': 'INVALID_STORE_NAME'
                }), 400

        # Validate watermark_url_image if provided
        if 'watermark_url_image' in data and data['watermark_url_image'] is not None:
            if not isinstance(data['watermark_url_image'], str) or not data['watermark_url_image'].strip():
                return jsonify({
                    'error': 'watermark_url_image must be a non-empty string',
                    'code': 'INVALID_IMAGE_URL'
                }), 400

        return None
