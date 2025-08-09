"""
Test script to verify the scraper with provided example cases.
"""
import requests
import json
import time

def test_api_endpoint(base_url, plate, vin, expected_result=None):
    """Test a specific API endpoint."""
    url = f"{base_url}/api/vehicular/tenencia/{plate}?niv={vin}"
    
    print(f"\nTesting: {plate} / {vin}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if expected_result:
                if result.get('codigo') == expected_result:
                    print("✅ Test PASSED")
                else:
                    print("❌ Test FAILED")
            else:
                print("ℹ️ Test completed (no expected result specified)")
        else:
            print(f"Non-JSON response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run test cases."""
    # Change this to your actual deployed URL or local server
    base_url = "http://localhost:5001"  # Change to your Heroku URL when deployed
    
    print("🧪 Testing Paga Fácil Vehicle Tax Scraper")
    print("=" * 50)
    
    # Test cases from the requirements
    test_cases = [
        {
            "plate": "GZG663J",
            "vin": "1VWBR7A39JC003850",
            "expected": "ok",
            "description": "Vehicle with no tax info"
        },
        {
            "plate": "HBE727F",
            "vin": "LJ12EKS36N4710772",
            "expected": "ok",
            "description": "Vehicle with tax information"
        },
        {
            "plate": "HAZ140G",
            "vin": "VSSFK46J2ER036480",
            "expected": "ok",
            "description": "Another vehicle with tax info"
        },
        {
            "plate": "HAW822H",
            "vin": "LJ12FKT35P4023393",
            "expected": "error",
            "description": "Invalid vehicle data"
        }
    ]
    
    # Test health check first
    print("\n🏥 Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check PASSED")
        else:
            print(f"❌ Health check FAILED: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check FAILED: {e}")
    
    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['description']}")
        test_api_endpoint(
            base_url, 
            test_case["plate"], 
            test_case["vin"], 
            test_case["expected"]
        )
        
        # Add delay between requests to be respectful
        if i < len(test_cases):
            print("⏱️ Waiting 2 seconds before next test...")
            time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")
    print("\nTo test with your deployed Heroku app, update the base_url variable")
    print("Example: base_url = 'https://your-app-name.herokuapp.com'")

if __name__ == "__main__":
    main()