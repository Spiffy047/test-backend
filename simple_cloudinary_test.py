#!/usr/bin/env python3
"""
Simple Cloudinary Configuration Test
Tests only the configuration endpoint that's currently available
"""

import requests
import json

# Live environment URL
BASE_URL = "https://hotfix.onrender.com"

def test_cloudinary_config():
    """Test Cloudinary configuration"""
    print("🔄 Testing Cloudinary Configuration...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/debug/cloudinary", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print("✅ Cloudinary Config SUCCESS!")
            print(f"   Cloud Name: {config.get('cloud_name', 'Not set')}")
            print(f"   API Key: {'✅ Set' if config.get('api_key') else '❌ Not set'}")
            print(f"   API Secret: {'✅ Set' if config.get('api_secret') else '❌ Not set'}")
            print(f"   Available: {'✅ Yes' if config.get('cloudinary_available') else '❌ No'}")
            
            # Check if all required config is present
            all_set = config.get('api_key') and config.get('api_secret') and config.get('cloud_name') != 'Not set'
            
            if all_set:
                print("\n🎉 CLOUDINARY IS FULLY CONFIGURED!")
                print("   Your environment variables are properly set on Render.")
                print("   Cloudinary upload/delete functionality should work once deployed.")
            else:
                print("\n⚠️  CLOUDINARY CONFIGURATION INCOMPLETE!")
                print("   Some environment variables are missing.")
            
            return all_set
        else:
            print("❌ Cloudinary Config FAILED!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Config Error: {e}")
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
    """Run simple Cloudinary configuration test"""
    print("=" * 60)
    print("🚀 CLOUDINARY CONFIGURATION TEST")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print("=" * 60)
    
    # Test 1: Health Check
    health_ok = test_health_check()
    
    print()
    
    # Test 2: Cloudinary Configuration
    config_ok = test_cloudinary_config()
    
    # Final Results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    if health_ok and config_ok:
        print("🎉 SUCCESS! Cloudinary is properly configured!")
        print("\n📋 Next Steps:")
        print("   1. Deploy the updated code with upload/delete endpoints")
        print("   2. Test actual file upload functionality")
        print("   3. Verify image transformations work as expected")
    elif health_ok:
        print("⚠️  PARTIAL SUCCESS - API is healthy but Cloudinary needs attention")
        print("\n📋 Action Required:")
        print("   1. Check Cloudinary environment variables on Render")
        print("   2. Verify CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")
    else:
        print("❌ FAILED - API health check failed")
        print("\n📋 Action Required:")
        print("   1. Check if the API is running")
        print("   2. Verify the URL is correct")
    
    print("=" * 60)

if __name__ == "__main__":
    main()