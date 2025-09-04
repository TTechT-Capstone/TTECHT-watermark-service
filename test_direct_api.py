#!/usr/bin/env python3
"""
Test script for direct API endpoints that bypass the controller layer.
This script demonstrates how to call the extract, embed, and detect services directly.

Usage:
    python test_direct_api.py

Make sure the Flask server is running on http://localhost:8000 before running this script.
"""

import requests
import json
import base64
from PIL import Image
import io
import os

# Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    'embed': f"{BASE_URL}/api/direct/embed",
    'extract': f"{BASE_URL}/api/direct/extract", 
    'detect': f"{BASE_URL}/api/direct/detect",
    'health': f"{BASE_URL}/api/direct/health"
}

def image_to_base64(image_path):
    """Convert image file to base64 string"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None

def create_test_images():
    """Create simple test images for demonstration"""
    # Create a simple test image (100x100 white with black text)
    test_img = Image.new('RGB', (100, 100), color='white')
    test_img.save('test_original.png')
    
    # Create a simple watermark (50x50 black with white text)
    watermark = Image.new('RGB', (50, 50), color='black')
    watermark.save('test_watermark.png')
    
    print("✅ Created test images: test_original.png, test_watermark.png")
    return 'test_original.png', 'test_watermark.png'

def test_health_check():
    """Test the health check endpoint"""
    print("\n🔍 Testing health check endpoint...")
    try:
        response = requests.get(API_ENDPOINTS['health'])
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_embed_watermark():
    """Test the direct embed watermark endpoint"""
    print("\n🔍 Testing direct embed watermark endpoint...")
    
    # Check if test images exist, create them if not
    if not os.path.exists('test_original.png') or not os.path.exists('test_watermark.png'):
        create_test_images()
    
    # Convert images to base64
    original_b64 = image_to_base64('test_original.png')
    watermark_b64 = image_to_base64('test_watermark.png')
    
    if not original_b64 or not watermark_b64:
        print("❌ Failed to convert images to base64")
        return None
    
    # Prepare payload
    payload = {
        "original_image": original_b64,
        "watermark_image": watermark_b64,
        "alpha": 0.6
    }
    
    try:
        response = requests.post(
            API_ENDPOINTS['embed'],
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Embed watermark successful")
            result = response.json()
            print(f"Unique ID: {result['data']['unique_id']}")
            print(f"Image size: {result['data']['image_size']}")
            return result['data']
        else:
            print(f"❌ Embed watermark failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Embed watermark error: {e}")
        return None

def test_extract_watermark(embed_result):
    """Test the direct extract watermark endpoint"""
    print("\n🔍 Testing direct extract watermark endpoint...")
    
    if not embed_result:
        print("❌ No embed result available for extraction test")
        return None
    
    # Get the suspect image (watermarked image) from embed result
    suspect_image_b64 = embed_result['watermarked_image']
    
    # Use the metadata from embedding as sideinfo
    sideinfo_json = embed_result['metadata']
    
    # Prepare payload
    payload = {
        "suspect_image": suspect_image_b64,
        "sideinfo_json": sideinfo_json
    }
    
    try:
        response = requests.post(
            API_ENDPOINTS['extract'],
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Extract watermark successful")
            result = response.json()
            print(f"Status: {result['status']}")
            if result['status'] == 'extracted':
                print(f"Extracted watermark ID: {result['data']['unique_id']}")
                print(f"Alpha: {result['data']['alpha']}")
                print(f"Wavelet: {result['data']['wavelet']}")
            return result['data']
        else:
            print(f"❌ Extract watermark failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Extract watermark error: {e}")
        return None

def test_detect_watermark(embed_result, extract_result):
    """Test the direct detect watermark endpoint"""
    print("\n🔍 Testing direct detect watermark endpoint...")
    
    if not embed_result or not extract_result:
        print("❌ Need both embed and extract results for detection test")
        return None
    
    # Get the original watermark and extracted watermark
    original_watermark_b64 = embed_result['metadata']['watermark_ref']['image_base64']
    extracted_watermark_b64 = extract_result.get('extracted_watermark')
    
    if not extracted_watermark_b64:
        print("❌ No extracted watermark available for detection test")
        return None
    
    # Prepare payload
    payload = {
        "original_watermark": original_watermark_b64,
        "extracted_watermark": extracted_watermark_b64,
        "pcc_threshold": 0.70,
        "save_record": False
    }
    
    try:
        response = requests.post(
            API_ENDPOINTS['detect'],
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Detect watermark successful")
            result = response.json()
            detection = result['data']['detection_result']
            metrics = result['data']['metrics']
            
            print(f"Detection result: {'✅ MATCH' if detection['is_match'] else '❌ NO MATCH'}")
            print(f"PCC: {metrics['pcc']:.4f}")
            print(f"|PCC|: {metrics['pcc_abs']:.4f}")
            print(f"MSE: {metrics['mse']:.4f}")
            print(f"SSIM: {metrics['ssim']:.4f}")
            print(f"PSNR: {metrics['psnr']:.2f} dB")
            
            return result['data']
        else:
            print(f"❌ Detect watermark failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Detect watermark error: {e}")
        return None

def cleanup_test_files():
    """Clean up test files"""
    test_files = ['test_original.png', 'test_watermark.png']
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️  Removed {file}")
            except Exception as e:
                print(f"⚠️  Could not remove {file}: {e}")

def main():
    """Main test function"""
    print("🚀 Testing Direct API Endpoints (bypassing controller layer)")
    print("=" * 60)
    
    # Test health check
    test_health_check()
    
    # Test embed watermark
    embed_result = test_embed_watermark()
    
    if embed_result:
        # Test extract watermark
        extract_result = test_extract_watermark(embed_result)
        
        if extract_result:
            # Test detect watermark
            detect_result = test_detect_watermark(embed_result, extract_result)
    
    print("\n" + "=" * 60)
    print("🏁 Direct API testing completed!")
    
    # Clean up test files
    cleanup_test_files()

if __name__ == "__main__":
    main()
