#!/usr/bin/env python3
"""
Test Cloudinary Upload with Real Image
"""

import requests
from io import BytesIO
from PIL import Image

def create_test_image():
    """Create a proper test image"""
    img = Image.new('RGB', (200, 200), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_upload():
    print("🔄 Testing Cloudinary Upload with Real Image...")
    
    # Create test image
    test_image = create_test_image()
    
    # Test data
    files = {
        'file': ('test_image.png', test_image, 'image/png')
    }
    
    data = {
        'ticket_id': '1001',
        'uploaded_by': 'test_user'
    }
    
    try:
        response = requests.post(
            "https://hotfix.onrender.com/api/test/cloudinary/upload",
            data=data,
            files=files,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"URL: {result.get('url')}")
            return result.get('public_id')
        else:
            print("❌ FAILED!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_upload()