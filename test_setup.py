#!/usr/bin/env python3
"""
Test script to verify the client-server setup
"""

import os
import sys
import requests
import time

def test_directory_structure():
    """Test if the directory structure is correct"""
    print("🔍 Testing directory structure...")
    
    required_dirs = ['client', 'server']
    required_files = [
        'client/static',
        'client/templates', 
        'server/app.py',
        'server/requirements.txt',
        'server/database.db',
        'docker-compose.yml',
        'Dockerfile'
    ]
    
    for item in required_dirs + required_files:
        if os.path.exists(item):
            print(f"✅ {item} exists")
        else:
            print(f"❌ {item} missing")
            return False
    
    return True

def test_flask_app_config():
    """Test if Flask app is configured correctly"""
    print("\n🔍 Testing Flask app configuration...")
    
    try:
        # Add server directory to path
        sys.path.insert(0, 'server')
        
        # Import the app
        from app import app
        
        # Check if template and static folders are set correctly
        if app.template_folder and 'client/templates' in app.template_folder:
            print("✅ Template folder configured correctly")
        else:
            print("❌ Template folder not configured correctly")
            return False
            
        if app.static_folder and 'client/static' in app.static_folder:
            print("✅ Static folder configured correctly")
        else:
            print("❌ Static folder not configured correctly")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing Flask app: {e}")
        return False

def test_docker_files():
    """Test if Docker files are properly configured"""
    print("\n🔍 Testing Docker configuration...")
    
    # Check docker-compose.yml
    if os.path.exists('docker-compose.yml'):
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
            if 'organ-donation-app' in content and '5000:5000' in content:
                print("✅ docker-compose.yml configured correctly")
            else:
                print("❌ docker-compose.yml not configured correctly")
                return False
    else:
        print("❌ docker-compose.yml missing")
        return False
    
    # Check Dockerfile
    if os.path.exists('Dockerfile'):
        with open('Dockerfile', 'r') as f:
            content = f.read()
            if 'COPY server/' in content and 'COPY client/' in content:
                print("✅ Dockerfile configured correctly")
            else:
                print("❌ Dockerfile not configured correctly")
                return False
    else:
        print("❌ Dockerfile missing")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Organ Donation Management System Setup\n")
    
    tests = [
        test_directory_structure,
        test_flask_app_config,
        test_docker_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Run: docker-compose up -d")
        print("2. Access: http://localhost:5000")
        print("3. Login with: admin@gmail.com / 1234")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
