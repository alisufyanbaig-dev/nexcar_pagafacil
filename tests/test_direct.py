#!/usr/bin/env python3
"""
Test script for PagaFacil scraper without proxy to verify basic functionality.
"""
import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import PagaFacilScraper

# Test just one case to start
TEST_CASE = {"plate": "FDH923C", "vin": "ML3AB56J7JH004905"}

def test_without_proxy():
    """Test scraper without proxy."""
    print("Testing PagaFacil Scraper WITHOUT proxy")
    print(f"Test case: {TEST_CASE['plate']} / {TEST_CASE['vin']}")
    print("="*60)
    
    try:
        # Initialize scraper without proxy
        scraper = PagaFacilScraper()
        print("✅ Scraper initialized successfully (no proxy)")
        
        # Test getting form data
        print("\n1. Testing form data retrieval...")
        form_data, captcha_image_path = scraper.get_form_data()
        print(f"✅ Form data retrieved: {list(form_data.keys())}")
        print(f"Captcha image path: {captcha_image_path}")
        
        # Test full vehicle query
        print(f"\n2. Testing vehicle query for {TEST_CASE['plate']}...")
        result = scraper.get_vehicle_info(TEST_CASE['plate'], TEST_CASE['vin'])
        
        print("\nResult:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_captcha_download():
    """Test just captcha image download."""
    print("\n" + "="*60)
    print("Testing captcha image download")
    print("="*60)
    
    try:
        scraper = PagaFacilScraper()
        
        # Get form data to find captcha
        form_data, captcha_image_path = scraper.get_form_data()
        
        if captcha_image_path:
            print(f"Found captcha at: {captcha_image_path}")
            
            # Try to solve captcha
            captcha_text = scraper.captcha_solver.solve_captcha(
                scraper.session, scraper.base_url, captcha_image_path
            )
            
            if captcha_text:
                print(f"✅ Captcha solved: {captcha_text}")
            else:
                print("❌ Failed to solve captcha")
                
            return captcha_text
        else:
            print("No captcha found")
            return None
            
    except Exception as e:
        print(f"❌ Error testing captcha: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function."""
    print("PagaFacil Direct Connection Test")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test basic functionality
    result = test_without_proxy()
    
    # Test captcha specifically
    captcha_result = test_captcha_download()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if result and result.get('codigo') == 'ok':
        print("✅ Vehicle query successful")
    elif result and 'captcha' in result.get('error', {}).get('mensaje', '').lower():
        print("⚠️  Vehicle query failed due to captcha issue")
    elif result:
        print("❌ Vehicle query failed")
    else:
        print("❌ Could not complete vehicle query")
    
    if captcha_result:
        print("✅ Captcha solving working")
    else:
        print("❌ Captcha solving needs improvement")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())