#!/usr/bin/env python3
"""
Test Cloudinary with curl and detailed error reporting
"""

import subprocess
import tempfile
import os
from PIL import Image

def create_test_image_file():
    """Create a temporary test image file"""
    img = Image.new('RGB', (100, 100), color='red')
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name, format='PNG')
    temp_file.close()
    
    return temp_file.name

def test_upload_with_curl():
    print("🔄 Testing Cloudinary Upload with curl...")
    
    # Create test image file
    image_file = create_test_image_file()
    
    try:
        # Use curl to upload
        cmd = [
            'curl', '-X', 'POST',
            'https://hotfix.onrender.com/api/test/cloudinary/upload',
            '-F', f'file=@{image_file}',
            '-F', 'ticket_id=1001',
            '-F', 'uploaded_by=test_user',
            '-v'  # Verbose output
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print(f"Exit code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up temp file
        if os.path.exists(image_file):
            os.unlink(image_file)

if __name__ == "__main__":
    test_upload_with_curl()