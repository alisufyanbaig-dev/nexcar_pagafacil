#!/usr/bin/env python3
"""
API test script for PagaFacil scraper REST endpoints.
"""
import requests
import json
import time
import sys
import os

# Test cases
TEST_CASES = [
    {"plate": "FDH923C", "vin": "ML3AB56J7JH004905"},  # Original failing case
    {"plate": "FKY171B", "vin": "3G1TA5AF1DL163526"},
    {"plate": "EWX819B", "vin": "MA6CB5CDXLT035912"},
]

BASE_URL = "http://localhost:5002"

def test_health_endpoint():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Health Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_status_endpoint():
    """Test detailed status endpoint."""
    print("\nTesting status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Status check failed: {e}")
        return False

def test_vehicular_endpoint(plate, vin):
    """Test vehicular endpoint with plate and VIN."""
    print(f"\nTesting vehicular endpoint: {plate} / {vin}")
    try:
        url = f"{BASE_URL}/api/vehicular/tenencia/{plate}?niv={vin}"
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        result = response.json()
        print(json.dumps(result, indent=2))
        
        return result.get('codigo') == 'ok'
    except Exception as e:
        print(f"API test failed: {e}")
        return False

def test_error_handling():
    """Test API error handling."""
    print("\nTesting error handling...")
    
    # Test missing VIN
    try:
        response = requests.get(f"{BASE_URL}/api/vehicular/tenencia/FDH923C", timeout=5)
        print(f"Missing VIN - Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error test failed: {e}")
    
    # Test invalid VIN
    try:
        response = requests.get(f"{BASE_URL}/api/vehicular/tenencia/INVALID?niv=INVALID", timeout=5)
        print(f"\nInvalid data - Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error test failed: {e}")

def main():
    """Main test function."""
    print("PagaFacil API Test Suite")
    print("=" * 50)
    
    # Test health endpoints
    health_ok = test_health_endpoint()
    status_ok = test_status_endpoint()
    
    if not (health_ok and status_ok):
        print("❌ Health checks failed. Make sure the server is running on port 5001")
        print("Start server with: python -m flask --app app run --port 5001")
        return 1
    
    # Test error handling
    test_error_handling()
    
    # Test vehicle endpoints
    success_count = 0
    print(f"\n{'=' * 50}")
    print("VEHICLE ENDPOINT TESTS")
    print(f"{'=' * 50}")
    
    for i, test_case in enumerate(TEST_CASES, 1):
        if test_vehicular_endpoint(test_case['plate'], test_case['vin']):
            success_count += 1
            print(f"✅ Test {i} PASSED")
        else:
            print(f"❌ Test {i} FAILED")
        
        # Delay between requests
        if i < len(TEST_CASES):
            time.sleep(2)
    
    # Summary
    print(f"\n{'=' * 50}")
    print("API TEST SUMMARY")
    print(f"{'=' * 50}")
    print(f"Health checks: {'✅ PASSED' if health_ok and status_ok else '❌ FAILED'}")
    print(f"Vehicle tests: {success_count}/{len(TEST_CASES)} passed")
    print(f"Success rate: {(success_count/len(TEST_CASES)*100):.1f}%")
    
    if success_count == len(TEST_CASES):
        print("\n🎉 ALL API TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  Some API tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())