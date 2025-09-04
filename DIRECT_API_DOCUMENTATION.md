# Direct API Documentation

This document describes the new direct API endpoints that bypass the controller layer and call the watermark services directly. These endpoints provide a more streamlined approach for applications that don't need the full controller functionality.

## Overview

The direct API endpoints are designed to:
- **Reduce latency** by eliminating the controller layer
- **Simplify the call stack** for direct service access
- **Maintain the same functionality** as the original endpoints
- **Provide better performance** for high-throughput applications

## Base URL

```
http://localhost:8000/api/direct
```

## Available Endpoints

### 1. Health Check

**Endpoint:** `GET /api/direct/health`

**Description:** Check the health status of the direct API service.

**Response:**
```json
{
  "status": "healthy",
  "service": "direct_api_service",
  "version": "1.0.0",
  "endpoints": {
    "embed": "/api/direct/embed",
    "extract": "/api/direct/extract",
    "detect": "/api/direct/detect"
  }
}
```

### 2. Embed Watermark

**Endpoint:** `POST /api/direct/embed`

**Description:** Embed a watermark into an original image using DWT and SVD algorithms.

**Request Body:**
```json
{
  "original_image": "base64_encoded_original_image",
  "watermark_image": "base64_encoded_watermark_image",
  "alpha": 0.6
}
```

**Parameters:**
- `original_image` (required): Base64 encoded original image
- `watermark_image` (required): Base64 encoded watermark image
- `alpha` (optional): Scaling factor for watermark embedding (default: 0.6, range: 0-1)

**Response:**
```json
{
  "success": true,
  "message": "Watermark embedded successfully",
  "data": {
    "watermarked_image": "base64_encoded_watermarked_image",
    "unique_id": "uuid_string",
    "image_size": [width, height],
    "metadata": {
      "wm_params": {
        "alpha": 0.6,
        "wavelet": "haar",
        "channels": "RGB"
      },
      "canonical_size": [width, height],
      "host_S": {
        "R": [singular_values_array],
        "G": [singular_values_array],
        "B": [singular_values_array]
      },
      "watermark_ref": {
        "image_base64": "base64_encoded_original_watermark",
        "resized_to": [width, height]
      }
    },
    "output_path": "/path/to/watermarked_image.jpg",
    "metadata_path": "/path/to/metadata.json"
  }
}
```

### 3. Extract Watermark

**Endpoint:** `POST /api/direct/extract`

**Description:** Extract a watermark from a suspect image using the original watermark and side information.

**Request Body:**
```json
{
  "suspect_image": "base64_encoded_suspect_image",
  "sideinfo_json": {
    "wm_params": {
      "alpha": 0.6,
      "wavelet": "haar",
      "channels": "RGB"
    },
    "canonical_size": [512, 512],
    "host_S": {
      "R": [singular_values_array],
      "G": [singular_values_array],
      "B": [singular_values_array]
    },
    "watermark_ref": {
      "image_base64": "base64_encoded_original_watermark_logo"
    }
  }
}
```

**Parameters:**
- `suspect_image` (required): Base64 encoded suspect image
- `sideinfo_json` (optional): Side information containing watermark parameters and original watermark

**Response (Successful Extraction):**
```json
{
  "success": true,
  "message": "Watermark extracted successfully",
  "status": "extracted",
  "data": {
    "extracted_watermark": "base64_encoded_extracted_watermark",
    "unique_id": "uuid_string",
    "alpha": 0.6,
    "wavelet": "haar",
    "canonical_size": [width, height],
    "sideinfo_used": "sideinfo_source",
    "watermark_logo": "watermark_source",
    "extracted_path": "/path/to/extracted_watermark.jpg"
  }
}
```

**Response (No Extraction Possible):**
```json
{
  "success": true,
  "message": "No watermark extraction possible - proceed with embedding",
  "status": "no_extraction",
  "reason": "Side-info not found/invalid. Proceed to embedding.",
  "data": {
    "proceed_to_embedding": true
  }
}
```

### 4. Detect Watermark

**Endpoint:** `POST /api/direct/detect`

**Description:** Compare original and extracted watermarks using statistical metrics to determine if they match.

**Request Body:**
```json
{
  "original_watermark": "base64_encoded_original_watermark",
  "extracted_watermark": "base64_encoded_extracted_watermark",
  "pcc_threshold": 0.70,
  "save_record": false,
  "suspect_image": "base64_encoded_suspect_image"
}
```

**Parameters:**
- `original_watermark` (required): Base64 encoded original watermark
- `extracted_watermark` (required): Base64 encoded extracted watermark
- `pcc_threshold` (optional): PCC threshold for detection (default: 0.70)
- `save_record` (optional): Whether to save detection record (default: false)
- `suspect_image` (optional): Base64 encoded suspect image for record saving

**Response:**
```json
{
  "success": true,
  "message": "Watermark detection completed successfully",
  "data": {
    "detection_result": {
      "is_match": true,
      "pcc_threshold": 0.70,
      "used_absolute_pcc": true
    },
    "metrics": {
      "pcc": 0.85,
      "pcc_abs": 0.85,
      "mse": 0.12,
      "ssim": 0.92,
      "psnr": 28.45
    },
    "comparison_results": {
      "pcc": 0.85,
      "pcc_abs": 0.85,
      "mse": 0.12,
      "ssim": 0.92,
      "psnr": 28.45
    },
    "detection_record": null
  }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

**Common Error Codes:**
- `INVALID_CONTENT_TYPE`: Request must be JSON
- `MISSING_BODY`: Request body is required
- `MISSING_FIELD`: Required field is missing
- `INVALID_IMAGE_DATA`: Invalid base64 image data
- `INVALID_ALPHA`: Alpha value must be between 0 and 1
- `INVALID_SIDEINFO_FORMAT`: Sideinfo must be a JSON object
- `MISSING_SIDEINFO_FIELD`: Required sideinfo field is missing
- `MISSING_WATERMARK_REFERENCE`: Watermark reference is missing
- `INVALID_BASE64_FORMAT`: Invalid base64 format
- `VALIDATION_ERROR`: General validation error
- `WATERMARK_EMBED_ERROR`: Watermark embedding error
- `WATERMARK_EXTRACT_ERROR`: Watermark extraction error
- `WATERMARK_DETECT_ERROR`: Watermark detection error

## Usage Examples

### Python Example

```python
import requests
import base64

# Convert image to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Embed watermark
def embed_watermark(original_image_path, watermark_image_path):
    url = "http://localhost:8000/api/direct/embed"
    
    payload = {
        "original_image": image_to_base64(original_image_path),
        "watermark_image": image_to_base64(watermark_image_path),
        "alpha": 0.6
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Extract watermark
def extract_watermark(suspect_image_b64, sideinfo_json):
    url = "http://localhost:8000/api/direct/extract"
    
    payload = {
        "suspect_image": suspect_image_b64,
        "sideinfo_json": sideinfo_json
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Detect watermark
def detect_watermark(original_watermark_b64, extracted_watermark_b64):
    url = "http://localhost:8000/api/direct/detect"
    
    payload = {
        "original_watermark": original_watermark_b64,
        "extracted_watermark": extracted_watermark_b64,
        "pcc_threshold": 0.70
    }
    
    response = requests.post(url, json=payload)
    return response.json()
```

### cURL Examples

**Health Check:**
```bash
curl -X GET http://localhost:8000/api/direct/health
```

**Embed Watermark:**
```bash
curl -X POST http://localhost:8000/api/direct/embed \
  -H "Content-Type: application/json" \
  -d '{
    "original_image": "base64_encoded_original_image",
    "watermark_image": "base64_encoded_watermark_image",
    "alpha": 0.6
  }'
```

**Extract Watermark:**
```bash
curl -X POST http://localhost:8000/api/direct/extract \
  -H "Content-Type: application/json" \
  -d '{
    "suspect_image": "base64_encoded_suspect_image",
    "sideinfo_json": {
      "wm_params": {"alpha": 0.6, "wavelet": "haar", "channels": "RGB"},
      "canonical_size": [512, 512],
      "host_S": {"R": [], "G": [], "B": []},
      "watermark_ref": {"image_base64": "base64_encoded_original_watermark"}
    }
  }'
```

**Detect Watermark:**
```bash
curl -X POST http://localhost:8000/api/direct/detect \
  -H "Content-Type: application/json" \
  -d '{
    "original_watermark": "base64_encoded_original_watermark",
    "extracted_watermark": "base64_encoded_extracted_watermark",
    "pcc_threshold": 0.70
  }'
```

## Performance Benefits

1. **Reduced Latency**: Eliminates controller layer processing
2. **Direct Service Access**: Services are called directly without intermediate validation layers
3. **Streamlined Processing**: Faster request handling for high-throughput applications
4. **Lower Memory Usage**: Fewer object instantiations

## Comparison with Original Endpoints

| Feature | Original Endpoints | Direct API Endpoints |
|---------|-------------------|---------------------|
| URL Pattern | `/api/images/*` | `/api/direct/*` |
| Architecture | Routes → Controller → Service | Routes → Service |
| Validation | Controller-level validation | Route-level validation |
| Performance | Standard | Enhanced |
| Use Case | Full application features | Direct service access |

## Testing

Use the provided `test_direct_api.py` script to test all endpoints:

```bash
python test_direct_api.py
```

Make sure the Flask server is running on `http://localhost:8000` before running the test script.

## Notes

- All endpoints maintain the same input/output format as the original endpoints
- Error handling is consistent across all endpoints
- The direct API is designed for applications that need direct service access
- For full application features, use the original endpoints through the controller layer
