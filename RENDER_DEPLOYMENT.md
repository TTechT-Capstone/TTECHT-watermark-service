# Render Deployment Guide for Watermark Service

## Overview
This guide helps you deploy the watermark service on Render with proper timeout configurations to handle image processing operations.

## Key Changes Made for Timeout Issues

### 1. Gunicorn Configuration
- **Timeout**: Set to 300 seconds (5 minutes) for image processing operations
- **Workers**: Configured for optimal performance
- **Memory Management**: Added worker recycling to prevent memory leaks

### 2. Application Timeout Handling
- Added thread-safe timeout decorators for long-running operations (using ThreadPoolExecutor)
- Implemented graceful timeout responses
- Added proper error handling for timeout scenarios
- Fixed signal-related issues by using concurrent.futures instead of signal module

### 3. Docker Configuration
- Updated Dockerfile to use gunicorn configuration file
- Optimized for production deployment

## Render Deployment Steps

### 1. Environment Variables
Set these environment variables in your Render dashboard:

```
ALLOWED_ORIGINS=https://your-frontend-domain.com
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
PORT=5000
WORKERS=1
PYTHONUNBUFFERED=1
```

### 2. Build Command
```bash
pip install -r requirements.txt
```

### 3. Start Command
```bash
gunicorn app:app -c gunicorn.conf.py
```

### 4. Render Service Configuration
- **Instance Type**: Choose at least "Starter" plan (512MB RAM minimum)
- **Auto-Deploy**: Enable for automatic deployments
- **Health Check Path**: `/health`

## Timeout Configuration Details

### Gunicorn Settings
- **Worker Timeout**: 300 seconds
- **Keep-Alive**: 5 seconds
- **Max Requests**: 1000 per worker
- **Graceful Timeout**: 30 seconds

### Application Timeouts
- **Embed Watermark**: 240 seconds (4 minutes)
- **Extract Watermark**: 240 seconds (4 minutes)
- **Request Size Limit**: 16MB

## Monitoring and Troubleshooting

### Health Check
The service provides a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy"
}
```

### Common Timeout Scenarios
1. **Large Images**: Images larger than 4MB may take longer to process
2. **Complex Watermarks**: High-resolution watermarks increase processing time
3. **Server Load**: High concurrent requests may cause delays

### Error Responses
The service returns appropriate HTTP status codes:
- **408**: Request timeout
- **413**: Request too large
- **500**: Internal server error

## Performance Optimization Tips

1. **Image Size**: Recommend images under 2MB for optimal performance
2. **Watermark Size**: Use watermarks that are 25-50% of the original image size
3. **Alpha Value**: Use values between 0.3-0.7 for best balance of visibility and processing speed

## Testing the Deployment

### Test Embed Watermark
```bash
curl -X POST https://your-service.onrender.com/api/direct/embed \
  -H "Content-Type: application/json" \
  -d '{
    "original_image": "base64_encoded_image",
    "watermark_image": "base64_encoded_watermark",
    "alpha": 0.6
  }'
```

### Test Extract Watermark
```bash
curl -X POST https://your-service.onrender.com/api/direct/extract \
  -H "Content-Type: application/json" \
  -d '{
    "suspect_image": "base64_encoded_image",
    "sideinfo_json": {
      "wm_params": {"alpha": 0.6, "wavelet": "haar", "channels": "RGB"},
      "canonical_size": [512, 512],
      "host_S": {"R": [], "G": [], "B": []},
      "watermark_ref": {
        "image_base64": "base64_encoded_watermark"
      }
    }
  }'
```

## Troubleshooting

### If you still get timeouts:
1. Check Render logs for specific error messages
2. Verify image sizes are within limits
3. Consider upgrading to a higher Render plan for more resources
4. Monitor memory usage in Render dashboard

### Common Issues:
- **Memory Issues**: Upgrade to a plan with more RAM
- **Cold Starts**: First request may be slower due to container startup
- **Network Issues**: Check if Cloudinary credentials are correct
