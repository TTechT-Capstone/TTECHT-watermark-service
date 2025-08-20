# controller/image_controller.py
from flask import request, jsonify
from service.image_service import ImageService
from service.embeded_service import EmbeddedService
from service.extract_service import ExtractService
from service.stat_detect import StatDetectService

class ImageController:
    def __init__(self):
        self.image_service = ImageService()
        self.embedded_service = EmbeddedService()
        self.extract_service = ExtractService()
        self.stat_detect_service = StatDetectService()

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

    def embed_watermark(self):
        """
        Handle watermark embedding request
        
        Expected JSON payload:
        {
            "original_image": "base64_encoded_original_image",
            "watermark_image": "base64_encoded_watermark_image",
            "alpha": 0.6  // optional, defaults to 0.6
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
            validation_error = self._validate_watermark_payload(data)
            if validation_error:
                return validation_error

            # Extract parameters
            original_image = data['original_image']
            watermark_image = data['watermark_image']
            alpha = float(data.get('alpha', 0.6))  # Default alpha value

            # Process watermark embedding through service
            result = self.embedded_service.embed_watermark_from_base64(
                original_image, 
                watermark_image, 
                alpha
            )
            
            return jsonify({
                'success': True,
                'message': 'Watermark embedded successfully',
                'data': {
                    'watermarked_image': result['watermarked_image_b64'],
                    'unique_id': result['unique_id'],
                    'image_size': result['image_size'],
                    'metadata': result['metadata'],
                    'output_path': result['output_path'],
                    'metadata_path': result['metadata_path']
                }
            }), 200

        except ValueError as e:
            return jsonify({
                'error': str(e),
                'code': 'VALIDATION_ERROR'
            }), 400

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'WATERMARK_EMBED_ERROR'
            }), 500

    def extract_watermark(self):
        """
        Handle watermark extraction request
        
        Expected JSON payload:
        {
            "suspect_image": "base64_encoded_suspect_image",
            "sideinfo_json_path": "/path/to/sideinfo.wm.json"  // optional
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
            validation_error = self._validate_extract_payload(data)
            if validation_error:
                return validation_error

            # Extract parameters
            suspect_image = data['suspect_image']
            raw_sideinfo = data.get('sideinfo_json_path', None)
            sideinfo_json_path = (raw_sideinfo or '').strip() or None


            # Process watermark extraction through service
            result = self.extract_service.extract_watermark_from_base64(
                suspect_image, 
                sideinfo_json_path
            )
            
            # Handle different extraction statuses
            if result["status"] == "ok_extracted":
                return jsonify({
                    'success': True,
                    'message': 'Watermark extracted successfully',
                    'status': 'extracted',
                    'data': {
                        'extracted_watermark': result.get('extracted_image_b64'),
                        'unique_id': result.get('unique_id'),
                        'alpha': result['alpha'],
                        'wavelet': result['wavelet'],
                        'canonical_size': result['canonical_size'],
                        'sideinfo_used': result['sideinfo_used'],
                        'watermark_logo': result['watermark_logo'],
                        'extracted_path': result['extracted_path'],
                        'suspect_save_path': result['suspect_save_path'],
                    }
                }), 200
            
            elif result["status"] in ["skip_no_sideinfo", "skip_bad_meta"]:
                return jsonify({
                    'success': True,
                    'message': 'No watermark extraction possible - proceed with embedding',
                    'status': 'no_extraction',
                    'reason': result['reason'],
                    'data': {
                        'proceed_to_embedding': True,
                        'suspect_save_path': result['suspect_save_path'],
                    }
                }), 200
            
            else:
                return jsonify({
                    'error': f"Unexpected extraction status: {result.get('status', 'unknown')}",
                    'code': 'EXTRACTION_ERROR'
                }), 500

        except ValueError as e:
            return jsonify({
                'error': str(e),
                'code': 'VALIDATION_ERROR'
            }), 400

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'WATERMARK_EXTRACT_ERROR'
            }), 500

    def detect_watermark(self):
        """
        Handle watermark detection/comparison request
        
        Expected JSON payload:
        {
            "original_watermark": "base64_encoded_original_watermark",
            "extracted_watermark": "base64_encoded_extracted_watermark",
            "pcc_threshold": 0.70,  // optional, defaults to 0.70
            "save_record": false,   // optional, defaults to false
            "suspect_image": "base64_encoded_suspect_image"  // optional, for record saving
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
            validation_error = self._validate_detect_payload(data)
            if validation_error:
                return validation_error

            # Extract parameters
            original_watermark = data['original_watermark']
            extracted_watermark = data['extracted_watermark']
            pcc_threshold = float(data.get('pcc_threshold', 0.70))
            save_record = bool(data.get('save_record', False))
            suspect_image = data.get('suspect_image', None)
            # Optional parameters
            matched_json_path = data.get('matched_json_path')  
            suspect_image_path = data.get('suspect_image_path')  


            # Process watermark detection through service
            result = self.stat_detect_service.compare_watermarks_from_base64(
                original_wm_b64=original_watermark,
                extracted_wm_b64=extracted_watermark,
                pcc_threshold=pcc_threshold,
                save_record=save_record,
                suspect_image_b64=suspect_image,
                matched_json_path=matched_json_path,
                suspect_image_path=suspect_image_path
            )
            
            return jsonify({
                'success': True,
                'message': 'Watermark detection completed successfully',
                'data': {
                    'detection_result': {
                        'is_match': result['detection']['is_match'],
                        'pcc_threshold': result['detection']['pcc_threshold'],
                        'used_absolute_pcc': result['detection']['used_absolute_pcc']
                    },
                    'metrics': result['metrics'],
                    'comparison_results': result['comparison_results'],
                    'detection_record': result.get('detection_record', None)
                }
            }), 200

        except ValueError as e:
            return jsonify({
                'error': str(e),
                'code': 'VALIDATION_ERROR'
            }), 400

        except Exception as e:
            return jsonify({
                'error': str(e),
                'code': 'WATERMARK_DETECT_ERROR'
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

    def _validate_watermark_payload(self, data):
        """
        Validate watermark embedding request payload
        
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

        if 'original_image' not in data:
            return jsonify({
                'error': 'Missing required field: original_image',
                'code': 'MISSING_FIELD'
            }), 400

        if 'watermark_image' not in data:
            return jsonify({
                'error': 'Missing required field: watermark_image',
                'code': 'MISSING_FIELD'
            }), 400

        if not data['original_image'] or not isinstance(data['original_image'], str):
            return jsonify({
                'error': 'original_image must be a non-empty base64 string',
                'code': 'INVALID_IMAGE_DATA'
            }), 400

        if not data['watermark_image'] or not isinstance(data['watermark_image'], str):
            return jsonify({
                'error': 'watermark_image must be a non-empty base64 string',
                'code': 'INVALID_IMAGE_DATA'
            }), 400

        # Validate alpha if provided
        if 'alpha' in data:
            alpha = data['alpha']
            if not isinstance(alpha, (int, float)) or alpha <= 0 or alpha > 1:
                return jsonify({
                    'error': 'alpha must be a number between 0 and 1',
                    'code': 'INVALID_ALPHA'
                }), 400

        return None

    def _validate_extract_payload(self, data):
        """
        Validate watermark extraction request payload
        
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

        if 'suspect_image' not in data:
            return jsonify({
                'error': 'Missing required field: suspect_image',
                'code': 'MISSING_FIELD'
            }), 400

        if not data['suspect_image'] or not isinstance(data['suspect_image'], str):
            return jsonify({
                'error': 'suspect_image must be a non-empty base64 string',
                'code': 'INVALID_IMAGE_DATA'
            }), 400

        # Validate sideinfo_json_path if provided
        if 'sideinfo_json_path' in data and data['sideinfo_json_path'] is not None:
            if not isinstance(data['sideinfo_json_path'], str):
                return jsonify({
                    'error': 'sideinfo_json_path must be a string',
                    'code': 'INVALID_PATH'
                }), 400

        return None

    def _validate_detect_payload(self, data):
        """
        Validate watermark detection request payload
        
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

        if 'original_watermark' not in data:
            return jsonify({
                'error': 'Missing required field: original_watermark',
                'code': 'MISSING_FIELD'
            }), 400

        if 'extracted_watermark' not in data:
            return jsonify({
                'error': 'Missing required field: extracted_watermark',
                'code': 'MISSING_FIELD'
            }), 400

        if not data['original_watermark'] or not isinstance(data['original_watermark'], str):
            return jsonify({
                'error': 'original_watermark must be a non-empty base64 string',
                'code': 'INVALID_IMAGE_DATA'
            }), 400

        if not data['extracted_watermark'] or not isinstance(data['extracted_watermark'], str):
            return jsonify({
                'error': 'extracted_watermark must be a non-empty base64 string',
                'code': 'INVALID_IMAGE_DATA'
            }), 400

        # Validate pcc_threshold if provided
        if 'pcc_threshold' in data:
            threshold = data['pcc_threshold']
            if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
                return jsonify({
                    'error': 'pcc_threshold must be a number between 0 and 1',
                    'code': 'INVALID_THRESHOLD'
                }), 400

        # Validate save_record if provided
        if 'save_record' in data and not isinstance(data['save_record'], bool):
            return jsonify({
                'error': 'save_record must be a boolean',
                'code': 'INVALID_BOOLEAN'
            }), 400

        # Validate suspect_image if provided
        if 'suspect_image' in data and data['suspect_image'] is not None:
            if not isinstance(data['suspect_image'], str) or not data['suspect_image']:
                return jsonify({
                    'error': 'suspect_image must be a non-empty base64 string when provided',
                    'code': 'INVALID_IMAGE_DATA'
                }), 400

        return None