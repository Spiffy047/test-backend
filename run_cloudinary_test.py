#!/usr/bin/env python3
"""
Quick Cloudinary Test Runner
Run this to test Cloudinary on your live environment
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages for testing"""
    packages = ['requests', 'Pillow']
    
    for package in packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def main():
    print("🚀 Cloudinary Test Setup")
    print("=" * 40)
    
    # Install requirements
    install_requirements()
    
    print("\n🔄 Running Cloudinary Test...")
    print("=" * 40)
    
    # Run the test
    try:
        result = subprocess.run([sys.executable, 'test_cloudinary_live.py'], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("\n✅ Test completed successfully!")
        else:
            print(f"\n❌ Test failed with return code: {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error running test: {e}")

if __name__ == "__main__":
    main()