#!/usr/bin/env python3
"""
Test Cloudinary directly with environment variables
"""

import os
import cloudinary
import cloudinary.uploader
from io import BytesIO
from PIL import Image

def test_direct_upload():
    print("🔄 Testing Cloudinary Direct Upload...")
    
    # Configure Cloudinary (these should match your Render environment)
    cloudinary.config(
        cloud_name="hotfix",  # Your cloud name from the config test
        api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET', '')
    )
    
    # Create test image
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    try:
        # Test upload
        result = cloudinary.uploader.upload(
            img_bytes,
            folder="servicedesk/tickets/test",
            public_id="test_upload"
        )
        
        print("✅ Direct upload successful!")
        print(f"URL: {result['secure_url']}")
        print(f"Public ID: {result['public_id']}")
        
        # Test delete
        delete_result = cloudinary.uploader.destroy(result['public_id'])
        print(f"Delete result: {delete_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Note: This won't work locally without the actual API keys
    # But it shows the correct approach
    print("This test requires actual Cloudinary API keys from your Render environment")
    print("The test structure is correct - the issue might be with environment variable access")
    
    # Show what the service should be doing
    print("\n📋 Expected Cloudinary Service Flow:")
    print("1. Get environment variables: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")
    print("2. Configure cloudinary with these values")
    print("3. Upload file to folder: servicedesk/tickets/{ticket_id}")
    print("4. Return secure_url, public_id, and metadata")
    
    # test_direct_upload()  # Uncomment if you have the keys locally