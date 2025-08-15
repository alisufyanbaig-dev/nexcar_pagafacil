#!/usr/bin/env python3
"""
Quick test script for PagaFacil scraper - tests 3 cases only for fast results.
"""
import sys
import os
import json
from datetime import datetime
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scraper_service import ScraperService

# Test just 3 cases for quick validation
TEST_CASES = [
    {"plate": "FDH923C", "vin": "ML3AB56J7JH004905"},  # Original failing case
    {"plate": "FKY171B", "vin": "3G1TA5AF1DL163526"},  # First test case
    {"plate": "EWX819B", "vin": "MA6CB5CDXLT035912"},  # Third test case
]

def test_single_case(scraper_service, plate, vin, case_number):
    """Test a single vehicle case."""
    print(f"\n{'='*50}")
    print(f"Test Case {case_number}: {plate} / {vin}")
    print(f"{'='*50}")
    
    try:
        result = scraper_service.get_vehicle_info(plate, vin)
        
        # Check if successful
        if result.get('codigo') == 'ok':
            print(f"✅ SUCCESS: Found vehicle information")
            return True
        elif result.get('codigo') == 'error':
            error_msg = result.get('error', {}).get('mensaje', 'Unknown error')
            print(f"❌ ERROR: {error_msg}")
            return False
        else:
            print(f"⚠️  UNKNOWN STATUS: {result.get('codigo')}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def main():
    """Main test function."""
    print("PagaFacil Scraper Quick Test")
    print(f"Testing {len(TEST_CASES)} vehicle cases")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Initialize scraper service without proxy
    try:
        scraper_service = ScraperService()
        print("✅ Scraper service initialized successfully (direct connection)")
    except Exception as e:
        print(f"❌ Failed to initialize scraper service: {e}")
        return 1
    
    # Test results
    success_count = 0
    
    # Run tests
    for i, test_case in enumerate(TEST_CASES, 1):
        plate = test_case['plate']
        vin = test_case['vin']
        
        if test_single_case(scraper_service, plate, vin, i):
            success_count += 1
        
        # Short delay between requests
        if i < len(TEST_CASES):
            print("Waiting 2 seconds...")
            time.sleep(2)
    
    # Print summary
    print(f"\n{'='*50}")
    print("QUICK TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Total test cases: {len(TEST_CASES)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(TEST_CASES) - success_count}")
    print(f"Success rate: {(success_count/len(TEST_CASES)*100):.1f}%")
    
    # Status assessment
    if success_count == len(TEST_CASES):
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   The scraper is working perfectly.")
        status_code = 0
    elif success_count >= len(TEST_CASES) * 0.67:  # 67% success rate
        print(f"\n✅ MOST TESTS PASSED")
        print(f"   The scraper is working well with {(success_count/len(TEST_CASES)*100):.1f}% success rate.")
        status_code = 0
    else:
        print(f"\n⚠️  TESTS FAILED")
        print(f"   Only {success_count}/{len(TEST_CASES)} tests passed.")
        status_code = 1
    
    return status_code

if __name__ == "__main__":
    sys.exit(main())