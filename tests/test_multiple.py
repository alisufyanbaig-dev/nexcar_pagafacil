#!/usr/bin/env python3
"""
Test script for PagaFacil scraper with multiple test cases (without proxy).
"""
import sys
import os
import json
from datetime import datetime
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import PagaFacilScraper

# Test a few cases to verify functionality
TEST_CASES = [
    {"plate": "FDH923C", "vin": "ML3AB56J7JH004905"},
    {"plate": "FKY171B", "vin": "3G1TA5AF1DL163526"},
    {"plate": "EWX819B", "vin": "MA6CB5CDXLT035912"},
    {"plate": "EVA834B", "vin": "3VW1K1AJ5HM277759"},
    {"plate": "FJF553A", "vin": "3N1CK3CD4FL240089"},
]

def test_single_case(scraper, plate, vin, case_number):
    """Test a single vehicle case."""
    print(f"\n{'='*60}")
    print(f"Test Case {case_number}: {plate} / {vin}")
    print(f"{'='*60}")
    
    try:
        result = scraper.get_vehicle_info(plate, vin)
        
        print("Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Check if successful
        if result.get('codigo') == 'ok':
            print(f"✅ SUCCESS: Found vehicle information")
            if result.get('info'):
                print(f"   Tax records found: {len(result['info'])}")
            if result.get('vehicle_info'):
                vehicle_info = result['vehicle_info']
                print(f"   Vehicle: {vehicle_info.get('make', 'N/A')} {vehicle_info.get('model', 'N/A')}")
                if vehicle_info.get('vin'):
                    print(f"   VIN: {vehicle_info['vin']}")
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
    print("PagaFacil Scraper Multi-Test (Direct Connection)")
    print(f"Testing {len(TEST_CASES)} vehicle cases")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Initialize scraper without proxy
    try:
        scraper = PagaFacilScraper()
        print("✅ Scraper initialized successfully (no proxy)")
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
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
        
        result = test_single_case(scraper, plate, vin, i)
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
        
        # Delay between requests to be respectful
        if i < len(TEST_CASES):
            print("Waiting 3 seconds before next test...")
            time.sleep(3)
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total test cases: {len(TEST_CASES)}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Captcha failures: {captcha_failures}")
    print(f"Success rate: {(success_count/len(TEST_CASES)*100):.1f}%")
    
    # Analyze failure patterns
    if error_count > 0:
        print(f"\nError Analysis:")
        error_messages = []
        for result_data in results:
            result = result_data['result']
            if result.get('codigo') == 'error':
                msg = result.get('error', {}).get('mensaje', 'Unknown')
                error_messages.append(msg)
        
        unique_errors = list(set(error_messages))
        for error in unique_errors:
            count = error_messages.count(error)
            print(f"  - {error}: {count} times")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_direct_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'proxy_used': False,
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