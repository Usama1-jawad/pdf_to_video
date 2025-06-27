#!/usr/bin/env python3
"""
Simple test script for the PDF to Video API
"""

import requests
import os

def test_health_endpoint(base_url):
    """Test the health endpoint"""
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health endpoint error: {e}")
        return False

def test_home_endpoint(base_url):
    """Test the home endpoint"""
    try:
        response = requests.get(base_url)
        print(f"Home endpoint status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Home endpoint error: {e}")
        return False

def test_upload_endpoint(base_url):
    """Test the upload endpoint with a sample PDF"""
    try:
        # Create a simple test PDF or use an existing one
        test_pdf_path = "test_sample.pdf"
        
        if not os.path.exists(test_pdf_path):
            print(f"Test PDF not found: {test_pdf_path}")
            print("Skipping upload test")
            return False
        
        with open(test_pdf_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/upload", files=files)
        
        print(f"Upload endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            # Save the video response
            with open("test_output.mp4", "wb") as f:
                f.write(response.content)
            print("Video saved as test_output.mp4")
        else:
            print(f"Upload failed: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Upload endpoint error: {e}")
        return False

def main():
    # Replace with your actual API URL
    base_url = "https://flipflow.onrender.com"
    
    print("Testing PDF to Video API...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    health_ok = test_health_endpoint(base_url)
    print()
    
    # Test home endpoint
    print("2. Testing home endpoint...")
    home_ok = test_home_endpoint(base_url)
    print()
    
    # Test upload endpoint (optional)
    print("3. Testing upload endpoint...")
    upload_ok = test_upload_endpoint(base_url)
    print()
    
    # Summary
    print("-" * 50)
    print("Test Summary:")
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Home endpoint: {'✅ PASS' if home_ok else '❌ FAIL'}")
    print(f"Upload endpoint: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    
    if health_ok and home_ok:
        print("\n🎉 API is working correctly!")
    else:
        print("\n⚠️  API has issues that need to be resolved.")

if __name__ == "__main__":
    main() 