#!/usr/bin/env python3
"""
Test script for PagaFacil scraper with provided test cases.
"""
import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scraper_service import ScraperService

# Test cases provided by user
TEST_CASES = [
    {"plate": "FKY171B", "vin": "3G1TA5AF1DL163526"},
    {"plate": "FBU219B", "vin": "3N1CK3CD9JL246205"},
    {"plate": "EWX819B", "vin": "MA6CB5CDXLT035912"},
    {"plate": "EVA834B", "vin": "3VW1K1AJ5HM277759"},
    {"plate": "FJF553A", "vin": "3N1CK3CD4FL240089"},
    {"plate": "EVA834B", "vin": "3VW1K1AJ5HM277759"},
    {"plate": "EWX819B", "vin": "MA6CB5CDXLT035912"},
    {"plate": "FAV455B", "vin": "3G1TA5AFXEL219027"},
    {"plate": "EVK879A", "vin": "9FBHS1FF3LM545124"},
    {"plate": "FPV2722", "vin": "3N1AB7AD7GL606775"},
    {"plate": "FCS206B", "vin": "3N1CN7AD2JL855041"},
    {"plate": "19E924", "vin": "LSJA24390RN030310"},
    {"plate": "EWX867D", "vin": "3GNCJ7CE9FL184819"},
    {"plate": "EWK531D", "vin": "1FATP8FF3G5263458"},
    {"plate": "FDH923C", "vin": "ML3AB56J7JH004905"},
    {"plate": "FAZ567D", "vin": "MA6CA6AD5HT028126"},
    {"plate": "EXU079D", "vin": "MEX5G2604KT033581"},
    {"plate": "FEH994C", "vin": "KL8MD6A01EC011238"},
    {"plate": "EYZ090D", "vin": "3N1CK3CD6KL208433"},
    {"plate": "EZL192D", "vin": "MAJFPIMDEGA124227"},
    {"plate": "FCT380C", "vin": "JN8BT27T8MW126609"},
    {"plate": "FPY2137", "vin": "3N8CP5HD6HL478150"},
    {"plate": "C1721527327", "vin": "19XFB268XCE602865"},
    {"plate": "US033", "vin": "3GNCJ7CE9GL15"},
    {"plate": "FNK134B", "vin": "3GNCJ7CE9FL184819"},
    {"plate": "FDE454D", "vin": "MRHGM6664HP053643"},
]

# Proxy configuration (these should be set from environment variables)
PROXY_HOST = os.getenv('PROXY_HOST', 'rotating-residential.proxyrack.net')
PROXY_PORT = int(os.getenv('PROXY_PORT', '9000'))
PROXY_USERNAME = os.getenv('PROXY_USERNAME', '0acb1d2c0b25b59cc5fc7bd6fcdbe9051bed8c78')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD', 'c1cc3b8b2e2b36e75a18cbe0b14d6e45e0b4fa6e')

def test_single_case(scraper_service, plate, vin, case_number):
    """Test a single vehicle case."""
    print(f"\n{'='*60}")
    print(f"Test Case {case_number}: {plate} / {vin}")
    print(f"{'='*60}")
    
    try:
        result = scraper_service.get_vehicle_info(plate, vin)
        
        print("Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Check if successful
        if result.get('codigo') == 'ok':
            print(f"✅ SUCCESS: Found vehicle information")
            if result.get('info'):
                print(f"   Tax records found: {len(result['info'])}")
        elif result.get('codigo') == 'error':
            print(f"❌ ERROR: {result.get('error', {}).get('mensaje', 'Unknown error')}")
        else:
            print(f"⚠️  UNKNOWN STATUS: {result.get('codigo')}")
            
        return result
        
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return {"codigo": "exception", "error": {"mensaje": str(e)}}

def main():
    """Main test function."""
    print("PagaFacil Scraper Test Suite")
    print(f"Testing {len(TEST_CASES)} vehicle cases")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Initialize scraper service
    try:
        # Try with proxy first
        if all([PROXY_HOST, PROXY_PORT, PROXY_USERNAME, PROXY_PASSWORD]):
            try:
                scraper_service = ScraperService(
                    proxy_host=PROXY_HOST,
                    proxy_port=PROXY_PORT,
                    proxy_username=PROXY_USERNAME,
                    proxy_password=PROXY_PASSWORD,
                    base_url="https://www.pagafacil.gob.mx/pagafacilv2/epago/cv/",
                    form_url="control_vehicular_25.php"
                )
                print("✅ Scraper service initialized successfully with proxy")
            except Exception as e:
                print(f"⚠️  Proxy initialization failed: {e}")
                print("Falling back to direct connection...")
                scraper_service = ScraperService()
                print("✅ Scraper service initialized successfully (direct connection)")
        else:
            scraper_service = ScraperService()
            print("✅ Scraper service initialized successfully (direct connection)")
    except Exception as e:
        print(f"❌ Failed to initialize scraper service: {e}")
        return 1
    
    # Test results summary
    results = []
    success_count = 0
    error_count = 0
    captcha_failures = 0
    
    # Run tests
    for i, test_case in enumerate(TEST_CASES, 1):
        plate = test_case['plate']
        vin = test_case['vin']
        
        result = test_single_case(scraper_service, plate, vin, i)
        results.append({
            'case': i,
            'plate': plate,
            'vin': vin,
            'result': result
        })
        
        # Count results
        if result.get('codigo') == 'ok':
            success_count += 1
        elif result.get('codigo') == 'error':
            error_count += 1
            if 'captcha' in result.get('error', {}).get('mensaje', '').lower():
                captcha_failures += 1
        
        # Short delay between requests to be respectful
        import time
        time.sleep(2)
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total test cases: {len(TEST_CASES)}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Captcha failures: {captcha_failures}")
    print(f"Success rate: {(success_count/len(TEST_CASES)*100):.1f}%")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_cases': len(TEST_CASES),
                'successful': success_count,
                'errors': error_count,
                'captcha_failures': captcha_failures,
                'success_rate': success_count/len(TEST_CASES)*100
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())