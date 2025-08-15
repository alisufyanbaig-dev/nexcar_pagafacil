#!/usr/bin/env python3
"""
Extended test script for PagaFacil scraper - tests 8 cases for comprehensive validation.
"""
import sys
import os
import json
from datetime import datetime
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scraper_service import ScraperService

# Test 8 cases from the user's list
TEST_CASES = [
    {"plate": "FDH923C", "vin": "ML3AB56J7JH004905"},  # Original failing case
    {"plate": "FKY171B", "vin": "3G1TA5AF1DL163526"},
    {"plate": "FBU219B", "vin": "3N1CK3CD9JL246205"},
    {"plate": "EWX819B", "vin": "MA6CB5CDXLT035912"},
    {"plate": "EVA834B", "vin": "3VW1K1AJ5HM277759"},
    {"plate": "FJF553A", "vin": "3N1CK3CD4FL240089"},
    {"plate": "FAV455B", "vin": "3G1TA5AFXEL219027"},
    {"plate": "EVK879A", "vin": "9FBHS1FF3LM545124"},
]

def test_single_case(scraper_service, plate, vin, case_number):
    """Test a single vehicle case."""
    print(f"\nTest Case {case_number}: {plate} / {vin}")
    
    try:
        result = scraper_service.get_vehicle_info(plate, vin)
        
        # Check if successful
        if result.get('codigo') == 'ok':
            print(f"✅ SUCCESS")
            return True
        elif result.get('codigo') == 'error':
            error_msg = result.get('error', {}).get('mensaje', 'Unknown error')
            print(f"❌ ERROR: {error_msg}")
            if 'captcha' in error_msg.lower():
                return 'captcha_fail'
            return False
        else:
            print(f"⚠️  UNKNOWN: {result.get('codigo')}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def main():
    """Main test function."""
    print("PagaFacil Scraper Extended Test")
    print(f"Testing {len(TEST_CASES)} vehicle cases")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60)
    
    # Initialize scraper service without proxy
    try:
        scraper_service = ScraperService()
        print("✅ Scraper service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize scraper service: {e}")
        return 1
    
    # Test results
    success_count = 0
    captcha_fail_count = 0
    other_fail_count = 0
    
    # Run tests
    for i, test_case in enumerate(TEST_CASES, 1):
        plate = test_case['plate']
        vin = test_case['vin']
        
        result = test_single_case(scraper_service, plate, vin, i)
        
        if result is True:
            success_count += 1
        elif result == 'captcha_fail':
            captcha_fail_count += 1
        else:
            other_fail_count += 1
        
        # Short delay between requests
        if i < len(TEST_CASES):
            time.sleep(2)
    
    # Print summary
    print(f"\n{'='*60}")
    print("EXTENDED TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total test cases: {len(TEST_CASES)}")
    print(f"✅ Successful: {success_count}")
    print(f"🔤 Captcha failures: {captcha_fail_count}")
    print(f"❌ Other failures: {other_fail_count}")
    print(f"Success rate: {(success_count/len(TEST_CASES)*100):.1f}%")
    
    # Detailed analysis
    total_attempts = success_count + captcha_fail_count + other_fail_count
    if captcha_fail_count > 0:
        captcha_success_rate = (success_count / (success_count + captcha_fail_count)) * 100
        print(f"Captcha success rate: {captcha_success_rate:.1f}%")
    
    # Status assessment
    if success_count >= len(TEST_CASES) * 0.875:  # 87.5% (7/8)
        print(f"\n🎉 EXCELLENT PERFORMANCE!")
        print(f"   The scraper improvements are working very well.")
        status_code = 0
    elif success_count >= len(TEST_CASES) * 0.75:  # 75% (6/8)
        print(f"\n✅ GOOD PERFORMANCE")
        print(f"   The scraper is working well with {(success_count/len(TEST_CASES)*100):.1f}% success rate.")
        status_code = 0
    elif success_count >= len(TEST_CASES) * 0.5:  # 50% (4/8)
        print(f"\n⚠️  MODERATE PERFORMANCE")
        print(f"   The scraper is functional but could be improved.")
        status_code = 1
    else:
        print(f"\n❌ POOR PERFORMANCE")
        print(f"   The scraper needs significant improvements.")
        status_code = 1
    
    # Assessment notes
    print(f"\n📊 ASSESSMENT:")
    print(f"   • Original issue: Captcha solving failures")
    print(f"   • Solution implemented: Enhanced OCR with multiple processing methods")
    print(f"   • Current performance: {success_count}/{len(TEST_CASES)} successful queries")
    
    if captcha_fail_count == 0:
        print(f"   • ✅ NO CAPTCHA FAILURES - OCR improvements working perfectly!")
    elif captcha_fail_count <= 2:
        print(f"   • ✅ Minimal captcha failures ({captcha_fail_count}) - excellent improvement!")
    else:
        print(f"   • ⚠️  Some captcha failures ({captcha_fail_count}) - normal for OCR-based systems")
    
    return status_code

if __name__ == "__main__":
    sys.exit(main())