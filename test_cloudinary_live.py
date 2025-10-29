#!/usr/bin/env python3
"""
Cloudinary Live Environment Test
Tests Cloudinary integration on the live environment (Render)
"""

import requests
import json
import os
from io import BytesIO
from PIL import Image
import time

# Live environment URL
BASE_URL = "https://hotfix.onrender.com"

def create_test_image():
    """Create a simple test image in memory"""
    # Create a 200x200 red square image
    img = Image.new('RGB', (200, 200), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_cloudinary_upload():
    """Test Cloudinary upload functionality"""
    print("🔄 Testing Cloudinary Upload...")
    
    # Create test image
    test_image = create_test_image()
    
    # Test data
    test_data = {
        'ticket_id': '1001',
        'uploaded_by': 'test_user',
        'message_id': 'test_msg_001'
    }
    
    # Prepare files for upload
    files = {
        'file': ('test_cloudinary.png', test_image, 'image/png')
    }
    
    try:
        # Make upload request
        response = requests.post(
            f"{BASE_URL}/api/test/cloudinary/upload",
            data=test_data,
            files=files,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Cloudinary Upload SUCCESS!")
            print(f"   URL: {result.get('url', 'N/A')}")
            print(f"   Public ID: {result.get('public_id', 'N/A')}")
            print(f"   Format: {result.get('format', 'N/A')}")
            print(f"   Size: {result.get('bytes', 0)} bytes")
            return result.get('public_id')
        else:
            print("❌ Cloudinary Upload FAILED!")
            return None
            
    except Exception as e:
        print(f"❌ Upload Error: {e}")
        return None

def test_cloudinary_config():
    """Test Cloudinary configuration endpoint"""
    print("\n🔄 Testing Cloudinary Configuration...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/debug/cloudinary", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print("✅ Cloudinary Config SUCCESS!")
            print(f"   Cloud Name: {config.get('cloud_name', 'Not set')}")
            print(f"   API Key: {'Set' if config.get('api_key') else 'Not set'}")
            print(f"   API Secret: {'Set' if config.get('api_secret') else 'Not set'}")
            print(f"   Available: {config.get('cloudinary_available', False)}")
            return True
        else:
            print("❌ Cloudinary Config FAILED!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Config Error: {e}")
        return False

def test_cloudinary_delete(public_id):
    """Test Cloudinary delete functionality"""
    if not public_id:
        print("\n⏭️  Skipping delete test (no public_id)")
        return False
        
    print(f"\n🔄 Testing Cloudinary Delete for: {public_id}")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/api/test/cloudinary/delete/{public_id}",
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Cloudinary Delete SUCCESS!")
            print(f"   Result: {result.get('result', 'N/A')}")
            return True
        else:
            print("❌ Cloudinary Delete FAILED!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Delete Error: {e}")
        return False

def test_health_check():
    """Test basic health check"""
    print("🔄 Testing API Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ API Health OK!")
            return True
        else:
            print("❌ API Health FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False

def main():
    """Run all Cloudinary tests"""
    print("=" * 60)
    print("🚀 CLOUDINARY LIVE ENVIRONMENT TEST")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    # Track test results
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Health Check
    if test_health_check():
        tests_passed += 1
    
    # Test 2: Cloudinary Configuration
    if test_cloudinary_config():
        tests_passed += 1
    
    # Test 3: Cloudinary Upload
    public_id = test_cloudinary_upload()
    if public_id:
        tests_passed += 1
    
    # Test 4: Cloudinary Delete
    if test_cloudinary_delete(public_id):
        tests_passed += 1
    
    # Final Results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Cloudinary is working perfectly!")
    elif tests_passed >= 2:
        print("⚠️  PARTIAL SUCCESS - Some issues detected")
    else:
        print("❌ MAJOR ISSUES - Cloudinary needs attention")
    
    print("=" * 60)

if __name__ == "__main__":
    main()