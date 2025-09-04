# routes/direct_api_routes.py
from flask import Blueprint, request, jsonify
from service.embeded_service import EmbeddedService
from service.extract_service import ExtractService
from service.stat_detect import StatDetectService
import base64

# Create blueprint for direct API calls
direct_api_bp = Blueprint('direct_api', __name__, url_prefix='/api/direct')

# Initialize services directly
embedded_service = EmbeddedService()
extract_service = ExtractService()
detect_service = StatDetectService()

# Direct Embed Watermark API
@direct_api_bp.route('/embed', methods=['POST'])
def direct_embed_watermark():
    """
    Direct API endpoint for embedding watermark - bypasses controller layer
    
    Expected JSON payload:
    {
        "original_image": "base64_encoded_original_image",
        "watermark_image": "base64_encoded_watermark_image",
        "alpha": 0.6  // optional, defaults to 0.6
    }
    
    Returns:
        JSON response with watermarked image and metadata
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
        alpha = data.get('alpha', 0.6)
        if not isinstance(alpha, (int, float)) or alpha <= 0 or alpha > 1:
            return jsonify({
                'error': 'alpha must be a number between 0 and 1',
                'code': 'INVALID_ALPHA'
            }), 400

        # Call service directly
        result = embedded_service.embed_watermark_from_base64(
            data['original_image'], 
            data['watermark_image'], 
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

# Direct Extract Watermark API
@direct_api_bp.route('/extract', methods=['POST'])
def direct_extract_watermark():
    """
    Direct API endpoint for extracting watermark - bypasses controller layer
    
    Expected JSON payload:
    {
        "suspect_image": "base64_encoded_suspect_image",
        "sideinfo_json": {  // optional - sideinfo with original watermark logo
            "wm_params": {"alpha": 0.6, "wavelet": "haar", "channels": "RGB"},
            "canonical_size": [512, 512],
            "host_S": {"R": [...], "G": [...], "B": [...]},
            "watermark_ref": {
                "image_base64": "base64_encoded_original_watermark_logo"
                // OR "path": "/path/to/original_watermark_logo.png" (for backward compatibility)
            }
        }
    }
    
    Returns:
        JSON response with extraction results
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

        # Validate sideinfo_json if provided
        sideinfo_json = data.get('sideinfo_json', None)
        if sideinfo_json is not None:
            if not isinstance(sideinfo_json, dict):
                return jsonify({
                    'error': 'sideinfo_json must be a JSON object',
                    'code': 'INVALID_SIDEINFO_FORMAT'
                }), 400
            
            # Validate required fields in sideinfo_json
            required_fields = ['wm_params', 'host_S', 'watermark_ref']
            for field in required_fields:
                if field not in sideinfo_json:
                    return jsonify({
                        'error': f'Missing required field in sideinfo_json: {field}',
                        'code': 'MISSING_SIDEINFO_FIELD'
                    }), 400
            
            # Validate watermark_ref has either path or image_base64
            watermark_ref = sideinfo_json['watermark_ref']
            has_path = 'path' in watermark_ref and watermark_ref['path']
            has_base64 = 'image_base64' in watermark_ref and watermark_ref['image_base64']
            
            if not has_path and not has_base64:
                return jsonify({
                    'error': 'watermark_ref must contain either "path" or "image_base64" field for the original watermark logo',
                    'code': 'MISSING_WATERMARK_REFERENCE'
                }), 400
            
            # Validate base64 format if provided
            if has_base64:
                try:
                    base64.b64decode(watermark_ref['image_base64'], validate=True)
                except Exception as e:
                    return jsonify({
                        'error': f'watermark_ref.image_base64 has invalid base64 format: {str(e)}',
                        'code': 'INVALID_BASE64_FORMAT'
                    }), 400

        # Call service directly
        result = extract_service.extract_watermark_from_base64_with_json(
            data['suspect_image'], 
            sideinfo_json
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
                    'extracted_path': result['extracted_path']
                }
            }), 200
        
        elif result["status"] in ["skip_no_sideinfo", "skip_bad_meta"]:
            return jsonify({
                'success': True,
                'message': 'No watermark extraction possible - proceed with embedding',
                'status': 'no_extraction',
                'reason': result['reason'],
                'data': {
                    'proceed_to_embedding': True
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

# Direct Detect Watermark API
@direct_api_bp.route('/detect', methods=['POST'])
def direct_detect_watermark():
    """
    Direct API endpoint for detecting/comparing watermarks - bypasses controller layer
    
    Expected JSON payload:
    {
        "original_watermark": "base64_encoded_original_watermark",
        "extracted_watermark": "base64_encoded_extracted_watermark",
        "pcc_threshold": 0.70,  // optional, defaults to 0.70
        "save_record": false,   // optional, defaults to false
        "suspect_image": "base64_encoded_suspect_image"  // optional, for record saving
    }
    
    Returns:
        JSON response with detection results and metrics
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
        
        # Extract parameters
        original_watermark = data.get('original_watermark')
        extracted_watermark = data.get('extracted_watermark')
        pcc_threshold = data.get('pcc_threshold', 0.70)
        save_record = data.get('save_record', False)
        suspect_image = data.get('suspect_image', None)

        # Basic validation
        if not original_watermark or not extracted_watermark:
            return jsonify({
                'error': 'Both original_watermark and extracted_watermark are required',
                'code': 'MISSING_FIELD'
            }), 400

        # Call service directly
        result = detect_service.compare_watermarks_from_base64(
            original_wm_b64=original_watermark,
            extracted_wm_b64=extracted_watermark,
            pcc_threshold=pcc_threshold,
            save_record=save_record,
            suspect_image_b64=suspect_image
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

# Health check for direct API
@direct_api_bp.route('/health', methods=['GET'])
def direct_health_check():
    """Direct health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'direct_api_service',
        'version': '1.0.0',
        'endpoints': {
            'embed': '/api/direct/embed',
            'extract': '/api/direct/extract',
            'detect': '/api/direct/detect'
        }
    }), 200

# Error handlers for the direct API blueprint
@direct_api_bp.errorhandler(404)
def direct_api_not_found(error):
    """Handle direct API endpoint not found error"""
    return jsonify({
        'error': 'Direct API endpoint not found',
        'code': 'DIRECT_API_ENDPOINT_NOT_FOUND'
    }), 404

@direct_api_bp.errorhandler(405)
def direct_api_method_not_allowed(error):
    """Handle method not allowed error for direct API"""
    return jsonify({
        'error': 'Method not allowed for direct API endpoint',
        'code': 'DIRECT_API_METHOD_NOT_ALLOWED'
    }), 405
