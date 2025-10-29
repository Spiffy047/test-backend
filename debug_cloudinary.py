#!/usr/bin/env python3
"""
Debug Cloudinary Service Locally
"""

import os
from io import BytesIO
from PIL import Image

# Set environment variables (you'll need to add your actual values)
os.environ['CLOUDINARY_CLOUD_NAME'] = 'hotfix'  # Replace with your actual cloud name
# os.environ['CLOUDINARY_API_KEY'] = 'your_api_key'
# os.environ['CLOUDINARY_API_SECRET'] = 'your_api_secret'

def test_cloudinary_service():
    try:
        from app.services.cloudinary_service import CloudinaryService
        
        # Create test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Test service
        service = CloudinaryService()
        result = service.upload_image(img_bytes, "test_ticket", "test_user")
        
        if result:
            print("✅ Cloudinary upload successful!")
            print(f"URL: {result['url']}")
            print(f"Public ID: {result['public_id']}")
        else:
            print("❌ Cloudinary upload failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cloudinary_service()