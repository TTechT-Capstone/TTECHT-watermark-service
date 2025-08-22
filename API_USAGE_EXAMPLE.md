# Watermark API Usage

This API provides both watermark embedding and extraction functionality using DWT (Discrete Wavelet Transform) and SVD (Singular Value Decomposition) algorithms, exactly as specified in your original logic.

## Installation

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

## API Endpoints

### 1. Watermark Embedding

**POST** `/api/images/embed-watermark`

### Request Format

```json
{
  "original_image": "base64_encoded_original_image_string",
  "watermark_image": "base64_encoded_watermark_image_string",
  "alpha": 0.6  // optional, default is 0.6 (scaling factor)
}
```

### Response Format

**Success (200):**
```json
{
  "success": true,
  "message": "Watermark embedded successfully",
  "data": {
    "watermarked_image": "base64_encoded_watermarked_image",
    "unique_id": "uuid-generated-id",
    "image_size": [width, height],
    "metadata": {
      "wm_params": {
        "alpha": 0.6,
        "wavelet": "haar",
        "channels": "RGB"
      },
      "canonical_size": [width, height],
      "output_path": "/path/to/saved/image.jpg",
      "ll_shapes": {
        "R": [height, width],
        "G": [height, width],
        "B": [height, width]
      },
      "host_S": {
        "R": [array_of_singular_values],
        "G": [array_of_singular_values],
        "B": [array_of_singular_values]
      },
      "watermark_ref": {
        "resized_to": [width, height]
      }
    },
    "output_path": "/path/to/watermarked_image.jpg",
    "metadata_path": "/path/to/metadata.wm.json"
  }
}
```

**Error (400/500):**
```json
{
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

### 2. Watermark Extraction

**POST** `/api/images/extract-watermark`

#### Request Format

```json
{
  "suspect_image": "base64_encoded_suspect_image_string",
  "sideinfo_json_path": "/path/to/sideinfo.wm.json"  // optional
}
```

#### Response Format

**Success - Watermark Extracted (200):**
```json
{
  "success": true,
  "message": "Watermark extracted successfully",
  "status": "extracted",
  "data": {
    "extracted_watermark": "base64_encoded_extracted_watermark",
    "unique_id": "generated_uuid",
    "alpha": 0.6,
    "wavelet": "haar",
    "canonical_size": [width, height],
    "sideinfo_used": "/path/to/used/sideinfo.wm.json",
    "watermark_logo": "/path/to/original/watermark/logo.jpg",
    "extracted_path": "/path/to/extracted/watermark.jpg"
  }
}
```

**Success - No Extraction Possible (200):**
```json
{
  "success": true,
  "message": "No watermark extraction possible - proceed with embedding",
  "status": "no_extraction",
  "reason": "No .wm.json provided/found for this image. Proceed to embedding.",
  "data": {
    "proceed_to_embedding": true
  }
}
```

**Error (400/500):**
```json
{
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

### 3. Watermark Detection/Comparison

**POST** `/api/images/detect-watermark`

### 4. Watermark Management (CRUD)

**POST** `/api/watermarks/` - Create watermark
**GET** `/api/watermarks/` - Get all watermarks
**GET** `/api/watermarks/<id>` - Get watermark by ID
**PUT** `/api/watermarks/<id>` - Update watermark
**DELETE** `/api/watermarks/<id>` - Delete watermark
**GET** `/api/watermarks/search?q=<query>` - Search watermarks

#### Request Format

```json
{
  "original_watermark": "base64_encoded_original_watermark_string",
  "extracted_watermark": "base64_encoded_extracted_watermark_string",
  "pcc_threshold": 0.70,  // optional, defaults to 0.70
  "save_record": false,   // optional, defaults to false
  "suspect_image": "base64_encoded_suspect_image_string"  // optional, for record saving
}
```

#### Response Format

**Success (200):**
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
      "mse": 123.45,
      "ssim": 0.92,
      "psnr": 28.5
    },
    "comparison_results": {
      "pcc": 0.85,
      "pcc_abs": 0.85,
      "mse": 123.45,
      "ssim": 0.92,
      "psnr": 28.5
    },
    "detection_record": {  // only present if save_record was true
      "record_id": "1234567890_abcd1234",
      "record_dir": "/tmp/detections/1234567890_abcd1234",
      "record_json": "/tmp/detections/1234567890_abcd1234/record.json",
      "created_at": 1234567890
    }
  }
}
```

**Error (400/500):**
```json
{
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

#### Watermark Management Endpoints

**Create Watermark:**
```json
{
  "store_name": "My Store",
  "watermark_url_image": "https://example.com/logo.png"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Watermark created successfully",
  "data": {
    "watermark_id": 1,
    "store_name": "My Store",
    "watermark_url_image": "https://example.com/logo.png"
  }
}
```

**Get All Watermarks Response:**
```json
{
  "success": true,
  "data": {
    "watermarks": [
      {
        "watermark_id": 1,
        "store_name": "My Store",
        "watermark_url_image": "https://example.com/logo.png"
      }
    ],
    "count": 1
  }
}
```

**Update Watermark:**
```json
{
  "store_name": "Updated Store Name",
  "watermark_url_image": "https://example.com/new-logo.png"
}
```

**Search Watermarks Response:**
```json
{
  "success": true,
  "data": {
    "query": "store",
    "watermarks": [
      {
        "watermark_id": 1,
        "store_name": "My Store",
        "watermark_url_image": "https://example.com/logo.png"
      }
    ],
    "count": 1
  }
}
```

## Example Usage with Python

### Embedding Example

```python
import requests
import base64

# Read images and convert to base64
with open("original_image.jpg", "rb") as f:
    original_b64 = base64.b64encode(f.read()).decode('utf-8')

with open("watermark_image.jpg", "rb") as f:
    watermark_b64 = base64.b64encode(f.read()).decode('utf-8')

# API request
url = "http://localhost:8000/api/images/embed-watermark"
payload = {
    "original_image": original_b64,
    "watermark_image": watermark_b64,
    "alpha": 0.6
}

response = requests.post(url, json=payload)
result = response.json()

if result["success"]:
    # Save watermarked image
    watermarked_b64 = result["data"]["watermarked_image"]
    watermarked_data = base64.b64decode(watermarked_b64)
    
    with open("watermarked_output.jpg", "wb") as f:
        f.write(watermarked_data)
    
    print("Watermarked image saved successfully!")
    print(f"Metadata: {result['data']['metadata']}")
else:
    print(f"Error: {result['error']}")
```

### Extraction Example

```python
import requests
import base64

# Read suspect image and convert to base64
with open("suspect_image.jpg", "rb") as f:
    suspect_b64 = base64.b64encode(f.read()).decode('utf-8')

# API request
url = "http://localhost:8000/api/images/extract-watermark"
payload = {
    "suspect_image": suspect_b64,
    # "sideinfo_json_path": "/path/to/sideinfo.wm.json"  # optional
}

response = requests.post(url, json=payload)
result = response.json()

if result["success"]:
    if result["status"] == "extracted":
        # Save extracted watermark
        extracted_b64 = result["data"]["extracted_watermark"]
        extracted_data = base64.b64decode(extracted_b64)
        
        with open("extracted_watermark.jpg", "wb") as f:
            f.write(extracted_data)
        
        print("Watermark extracted successfully!")
        print(f"Alpha used: {result['data']['alpha']}")
        print(f"Wavelet used: {result['data']['wavelet']}")
    
    elif result["status"] == "no_extraction":
        print("No watermark found - can proceed with embedding")
        print(f"Reason: {result['reason']}")
else:
    print(f"Error: {result['error']}")
```

### Detection Example

```python
import requests
import base64

# Read original watermark and extracted watermark and convert to base64
with open("original_watermark.jpg", "rb") as f:
    original_wm_b64 = base64.b64encode(f.read()).decode('utf-8')

with open("extracted_watermark.jpg", "rb") as f:
    extracted_wm_b64 = base64.b64encode(f.read()).decode('utf-8')

# API request
url = "http://localhost:8000/api/images/detect-watermark"
payload = {
    "original_watermark": original_wm_b64,
    "extracted_watermark": extracted_wm_b64,
    "pcc_threshold": 0.70,
    "save_record": True  # Save detection record for admin
}

response = requests.post(url, json=payload)
result = response.json()

if result["success"]:
    detection = result["data"]["detection_result"]
    metrics = result["data"]["metrics"]
    
    print(f"Detection Result: {'MATCH' if detection['is_match'] else 'NO MATCH'}")
    print(f"PCC: {metrics['pcc']:.4f}")
    print(f"|PCC|: {metrics['pcc_abs']:.4f}")
    print(f"MSE: {metrics['mse']:.2f}")
    print(f"SSIM: {metrics['ssim']:.4f}")
    print(f"PSNR: {metrics['psnr']:.2f} dB")
    
    if "detection_record" in result["data"]:
        record = result["data"]["detection_record"]
        print(f"Detection record saved: {record['record_id']}")
else:
    print(f"Error: {result['error']}")
```

### Watermark Management Examples

```python
import requests

# Create a new watermark
url = "http://localhost:8000/api/watermarks/"
payload = {
    "store_name": "My Store",
    "watermark_url_image": "https://example.com/logo.png"
}

response = requests.post(url, json=payload)
result = response.json()

if result["success"]:
    watermark = result["data"]
    print(f"Watermark created with ID: {watermark['watermark_id']}")
    print(f"Store: {watermark['store_name']}")
    print(f"Image URL: {watermark['watermark_url_image']}")
else:
    print(f"Error: {result['error']}")

# Get all watermarks
response = requests.get("http://localhost:8000/api/watermarks/")
result = response.json()

if result["success"]:
    watermarks = result["data"]["watermarks"]
    print(f"Found {len(watermarks)} watermarks:")
    for wm in watermarks:
        print(f"  ID: {wm['watermark_id']}, Store: {wm['store_name']}")

# Search watermarks
query = "store"
response = requests.get(f"http://localhost:8000/api/watermarks/search?q={query}")
result = response.json()

if result["success"]:
    matches = result["data"]["watermarks"]
    print(f"Found {len(matches)} watermarks matching '{query}'")

# Update watermark
watermark_id = 1
update_payload = {
    "store_name": "Updated Store Name"
}

response = requests.put(f"http://localhost:8000/api/watermarks/{watermark_id}", 
                       json=update_payload)
result = response.json()

if result["success"]:
    print("Watermark updated successfully")

# Delete watermark
watermark_id = 1
response = requests.delete(f"http://localhost:8000/api/watermarks/{watermark_id}")
result = response.json()

if result["success"]:
    print("Watermark deleted successfully")
```

## Example Usage with cURL

### Embedding

```bash
curl -X POST http://localhost:8000/api/images/embed-watermark \
  -H "Content-Type: application/json" \
  -d '{
    "original_image": "your_base64_original_image_here",
    "watermark_image": "your_base64_watermark_image_here",
    "alpha": 0.6
  }'
```

### Extraction

```bash
curl -X POST http://localhost:8000/api/images/extract-watermark \
  -H "Content-Type: application/json" \
  -d '{
    "suspect_image": "your_base64_suspect_image_here",
    "sideinfo_json_path": "/path/to/sideinfo.wm.json"
  }'
```

### Detection

```bash
curl -X POST http://localhost:8000/api/images/detect-watermark \
  -H "Content-Type: application/json" \
  -d '{
    "original_watermark": "your_base64_original_watermark_here",
    "extracted_watermark": "your_base64_extracted_watermark_here",
    "pcc_threshold": 0.70,
    "save_record": true
  }'
```

### Watermark Management

```bash
# Create watermark
curl -X POST http://localhost:8000/api/watermarks/ \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "My Store",
    "watermark_url_image": "https://example.com/logo.png"
  }'

# Get all watermarks
curl -X GET http://localhost:8000/api/watermarks/

# Get watermark by ID
curl -X GET http://localhost:8000/api/watermarks/1

# Search watermarks
curl -X GET "http://localhost:8000/api/watermarks/search?q=store"

# Update watermark
curl -X PUT http://localhost:8000/api/watermarks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "Updated Store Name"
  }'

# Delete watermark
curl -X DELETE http://localhost:8000/api/watermarks/1
```

## Algorithm Details

### Embedding Process

The API implements your exact watermark embedding logic:

1. **Image Preprocessing**: Both images are converted to RGB and the watermark is resized to match the original image size
2. **Channel Separation**: Each image is split into Red, Green, and Blue channels
3. **DWT Transform**: 1-level Haar Discrete Wavelet Transform is applied to each channel
4. **SVD Decomposition**: Singular Value Decomposition is performed on the LL (low-frequency) sub-bands
5. **Watermark Embedding**: The watermark is embedded using the formula: `S_modified = S_original + alpha * S_watermark`
6. **Reconstruction**: The modified image is reconstructed using Inverse DWT
7. **Normalization**: Final image is normalized to 0-255 uint8 format

### Extraction Process

The API implements your exact watermark extraction logic:

1. **Auto-Detection**: If no sideinfo path is provided, the system uses perceptual hashing (pHash) to find the best matching watermarked image in the database
2. **Metadata Loading**: Loads the corresponding `.wm.json` file containing embedding parameters and SVD values
3. **Image Loading**: Loads both the suspect image and the original watermark logo
4. **Size Normalization**: Resizes images to canonical size from embedding metadata
5. **Channel Processing**: Processes each RGB channel separately for extraction
6. **DWT & SVD**: Applies DWT and SVD to extract embedded information
7. **Semi-Blind Extraction**: Uses the formula: `S_extracted = (S_suspect - S_original) / alpha`
8. **Reconstruction**: Reconstructs the extracted watermark using Inverse DWT

### Detection Process

The API implements your exact statistical detection logic:

1. **Image Loading**: Loads both original and extracted watermark images from base64
2. **Grayscale Conversion**: Converts images to grayscale for analysis
3. **Size Normalization**: Resizes extracted image to match original if needed
4. **Statistical Metrics**: Calculates multiple comparison metrics:
   - **PCC (Pearson Correlation Coefficient)**: Main metric for unauthorized usage detection
   - **|PCC|**: Absolute value used for detection (handles reversed colors)
   - **MSE (Mean Squared Error)**: Pixel-level difference measurement
   - **SSIM (Structural Similarity Index)**: Perceptual similarity measurement
   - **PSNR (Peak Signal-to-Noise Ratio)**: Quality measurement in dB
5. **Threshold Comparison**: Uses PCC absolute value against configurable threshold (default: 0.70)
6. **Record Saving**: Optional admin record with all metrics and image copies

## Error Codes

### Common Error Codes

- `INVALID_CONTENT_TYPE`: Request must be JSON
- `MISSING_BODY`: Request body is required
- `MISSING_FIELD`: Required field missing (original_image or watermark_image)
- `INVALID_IMAGE_DATA`: Invalid base64 image data
- `INVALID_ALPHA`: Alpha must be between 0 and 1
- `VALIDATION_ERROR`: General validation error
- `WATERMARK_EMBED_ERROR`: Error during watermark embedding process

### Extraction-Specific Error Codes

- `WATERMARK_EXTRACT_ERROR`: Error during watermark extraction process
- `EXTRACTION_ERROR`: Unexpected extraction status
- `INVALID_PATH`: Invalid sideinfo JSON path

### Detection-Specific Error Codes

- `WATERMARK_DETECT_ERROR`: Error during watermark detection/comparison process
- `INVALID_THRESHOLD`: PCC threshold must be between 0 and 1
- `INVALID_BOOLEAN`: Boolean parameter validation error

### Watermark Management Error Codes

- `WATERMARK_CREATE_ERROR`: Error during watermark creation
- `WATERMARK_RETRIEVAL_ERROR`: Error during watermark retrieval
- `WATERMARK_UPDATE_ERROR`: Error during watermark update
- `WATERMARK_DELETE_ERROR`: Error during watermark deletion
- `WATERMARK_SEARCH_ERROR`: Error during watermark search
- `WATERMARK_NOT_FOUND`: Watermark with specified ID not found
- `INVALID_STORE_NAME`: Invalid store name format
- `INVALID_IMAGE_URL`: Invalid watermark image URL
- `MISSING_FIELDS`: No fields provided for update
- `MISSING_QUERY`: Search query parameter missing

## Workflow Integration

The API is designed to support a comprehensive watermarking workflow:

### Full Detection & Protection Workflow

1. **Try Extraction First**: Call `/extract-watermark` to check if the image already contains a watermark
2. **Handle Extraction Results**:
   - If `status: "extracted"` → watermark found and extracted successfully, proceed to step 3
   - If `status: "no_extraction"` → no watermark detected, proceed to embedding (step 5)
3. **Compare Watermarks**: Call `/detect-watermark` with original and extracted watermarks
4. **Handle Detection Results**:
   - If `is_match: true` → unauthorized usage detected (take appropriate action)
   - If `is_match: false` → different/no watermark detected
5. **Embed If Needed**: If no watermark found, call `/embed-watermark` to add protection

### Metrics Interpretation

- **PCC ≥ 0.70**: Strong correlation indicating likely unauthorized usage
- **|PCC|**: Uses absolute value to handle reversed/inverted watermarks
- **SSIM > 0.8**: High structural similarity
- **High PSNR**: Better quality preservation
- **Low MSE**: Lower pixel-level differences

This comprehensive approach allows for intelligent detection of unauthorized image usage while providing robust watermark protection.

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:8000`
