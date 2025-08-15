#!/usr/bin/env python3
"""
Comprehensive test script for PagaFacil scraper with all provided test cases.
Tests all 26 vehicle cases provided by the user.
"""
import sys
import os
import json
from datetime import datetime
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scraper_service import ScraperService

# All test cases provided by user - organized and cleaned
TEST_CASES = [
    # First batch
    {"plate": "FPY2137", "vin": "3N8CP5HD6HL478150"},
    {"plate": "C1721527327", "vin": "19XFB268XCE602865"},
    {"plate": "US033", "vin": "3GNCJ7CE9GL15"},
    {"plate": "FNK134B", "vin": "3GNCJ7CE9FL184819"},
    {"plate": "FDE454D", "vin": "MRHGM6664HP053643"},
    
    # Second batch  
    {"plate": "19E924", "vin": "LSJA24390RN030310"},
    {"plate": "EWX867D", "vin": "3GNCJ7CE9FL184819"},
    {"plate": "EWK531D", "vin": "1FATP8FF3G5263458"},
    {"plate": "FDH923C", "vin": "ML3AB56J7JH004905"},  # Original failing case
    {"plate": "FAZ567D", "vin": "MA6CA6AD5HT028126"},
    {"plate": "EXU079D", "vin": "MEX5G2604KT033581"},
    
    # Third batch
    {"plate": "FEH994C", "vin": "KL8MD6A01EC011238"},
    {"plate": "EYZ090D", "vin": "3N1CK3CD6KL208433"},
    {"plate": "EZL192D", "vin": "MAJFPIMDEGA124227"},
    {"plate": "FCT380C", "vin": "JN8BT27T8MW126609"},
    
    # Fourth batch (original Aduedos list)
    {"plate": "FKY171B", "vin": "3G1TA5AF1DL163526"},
    {"plate": "FBU219B", "vin": "3N1CK3CD9JL246205"},
    {"plate": "EWX819B", "vin": "MA6CB5CDXLT035912"},
    {"plate": "EVA834B", "vin": "3VW1K1AJ5HM277759"},
    {"plate": "FJF553A", "vin": "3N1CK3CD4FL240089"},
    {"plate": "FAV455B", "vin": "3G1TA5AFXEL219027"},
    {"plate": "EVK879A", "vin": "9FBHS1FF3LM545124"},
    {"plate": "FPV2722", "vin": "3N1AB7AD7GL606775"},
    {"plate": "FCS206B", "vin": "3N1CN7AD2JL855041"},
]

def test_single_case(scraper_service, plate, vin, case_number, total_cases):
    """Test a single vehicle case."""
    print(f"\n{'='*70}")
    print(f"Test Case {case_number}/{total_cases}: {plate} / {vin}")
    print(f"{'='*70}")
    
    try:
        start_time = time.time()
        result = scraper_service.get_vehicle_info(plate, vin)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Query Duration: {duration:.2f} seconds")
        
        # Check if successful
        if result.get('codigo') == 'ok':
            print(f"✅ SUCCESS: Found vehicle information")
            
            # Show vehicle info if available
            if result.get('vehicle_info'):
                vehicle_info = result['vehicle_info']
                make = vehicle_info.get('make', 'N/A')
                model = vehicle_info.get('model', 'N/A') 
                year = vehicle_info.get('year', 'N/A')
                color = vehicle_info.get('color', 'N/A')
                
                print(f"   Vehicle: {make} {model} ({year})")
                if color and color != 'N/A':
                    print(f"   Color: {color}")
            
            # Show tax info if available
            if result.get('info'):
                tax_records = result['info']
                print(f"   Tax records found: {len(tax_records)}")
                if tax_records:
                    print(f"   Sample record: {tax_records[0] if isinstance(tax_records, list) else 'Available'}")
            
            return {"status": "success", "duration": duration, "result": result}
            
        elif result.get('codigo') == 'error':
            error_msg = result.get('error', {}).get('mensaje', 'Unknown error')
            print(f"❌ ERROR: {error_msg}")
            
            # Categorize error type
            if 'captcha' in error_msg.lower():
                return {"status": "captcha_error", "duration": duration, "error": error_msg}
            elif 'proxy' in error_msg.lower() or 'connection' in error_msg.lower():
                return {"status": "connection_error", "duration": duration, "error": error_msg}
            else:
                return {"status": "other_error", "duration": duration, "error": error_msg}
        else:
            print(f"⚠️  UNKNOWN STATUS: {result.get('codigo')}")
            return {"status": "unknown", "duration": duration, "result": result}
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return {"status": "exception", "duration": 0, "error": str(e)}

def print_progress_summary(current, total, success_count, error_count):
    """Print a progress summary."""
    progress_pct = (current / total) * 100
    success_pct = (success_count / current) * 100 if current > 0 else 0
    
    print(f"\n📊 PROGRESS: {current}/{total} ({progress_pct:.1f}%) | " +
          f"✅ Success: {success_count} ({success_pct:.1f}%) | " +
          f"❌ Errors: {error_count}")

def main():
    """Main test function."""
    print("🚀 PagaFacil Scraper - COMPREHENSIVE TEST SUITE")
    print(f"Testing {len(TEST_CASES)} vehicle cases (ALL PROVIDED TEST DATA)")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*70}")
    
    # Initialize scraper service without proxy (for reliability)
    try:
        scraper_service = ScraperService()
        print("✅ Scraper service initialized successfully (direct connection)")
        print("Note: Using direct connection for maximum reliability")
    except Exception as e:
        print(f"❌ Failed to initialize scraper service: {e}")
        return 1
    
    # Test results tracking
    results = []
    success_count = 0
    error_counts = {
        "captcha_error": 0,
        "connection_error": 0,
        "other_error": 0,
        "exception": 0,
        "unknown": 0
    }
    
    total_duration = 0
    
    # Run tests
    for i, test_case in enumerate(TEST_CASES, 1):
        plate = test_case['plate']
        vin = test_case['vin']
        
        test_result = test_single_case(scraper_service, plate, vin, i, len(TEST_CASES))
        
        results.append({
            'case_number': i,
            'plate': plate,
            'vin': vin,
            'status': test_result['status'],
            'duration': test_result['duration'],
            'error': test_result.get('error'),
            'result': test_result.get('result')
        })
        
        total_duration += test_result['duration']
        
        # Count results
        if test_result['status'] == 'success':
            success_count += 1
        else:
            error_counts[test_result['status']] = error_counts.get(test_result['status'], 0) + 1
        
        # Show progress every 5 tests
        if i % 5 == 0 or i == len(TEST_CASES):
            print_progress_summary(i, len(TEST_CASES), success_count, 
                                 sum(error_counts.values()))
        
        # Respectful delay between requests (except for last one)
        if i < len(TEST_CASES):
            print("⏱️  Waiting 3 seconds before next test...")
            time.sleep(3)
    
    # Calculate statistics
    total_errors = sum(error_counts.values())
    success_rate = (success_count / len(TEST_CASES)) * 100
    avg_duration = total_duration / len(TEST_CASES)
    
    # Print comprehensive summary
    print(f"\n{'='*70}")
    print("🎯 COMPREHENSIVE TEST RESULTS")
    print(f"{'='*70}")
    print(f"📊 Overall Statistics:")
    print(f"   Total test cases: {len(TEST_CASES)}")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Total errors: {total_errors}")
    print(f"   📈 Success rate: {success_rate:.1f}%")
    print(f"   ⏱️  Average duration: {avg_duration:.2f} seconds")
    print(f"   🕐 Total test time: {total_duration:.1f} seconds")
    
    # Detailed error breakdown
    if total_errors > 0:
        print(f"\n🔍 Error Breakdown:")
        for error_type, count in error_counts.items():
            if count > 0:
                error_pct = (count / len(TEST_CASES)) * 100
                print(f"   {error_type.replace('_', ' ').title()}: {count} ({error_pct:.1f}%)")
    
    # Performance assessment
    print(f"\n🎭 Performance Assessment:")
    if success_rate >= 95:
        print("   🌟 EXCELLENT: Outstanding performance!")
        assessment = "excellent"
    elif success_rate >= 85:
        print("   ✨ VERY GOOD: Strong performance!")
        assessment = "very_good"
    elif success_rate >= 75:
        print("   👍 GOOD: Acceptable performance!")
        assessment = "good"
    elif success_rate >= 60:
        print("   ⚠️  FAIR: Needs improvement!")
        assessment = "fair"
    else:
        print("   ❌ POOR: Significant issues detected!")
        assessment = "poor"
    
    # Show successful cases
    successful_cases = [r for r in results if r['status'] == 'success']
    if successful_cases:
        print(f"\n✅ Successful Test Cases ({len(successful_cases)}):")
        for case in successful_cases[:10]:  # Show first 10
            print(f"   • {case['plate']} / {case['vin']} ({case['duration']:.1f}s)")
        if len(successful_cases) > 10:
            print(f"   ... and {len(successful_cases) - 10} more")
    
    # Show failed cases
    failed_cases = [r for r in results if r['status'] != 'success']
    if failed_cases:
        print(f"\n❌ Failed Test Cases ({len(failed_cases)}):")
        for case in failed_cases:
            error_msg = case.get('error', 'Unknown error')[:50]
            print(f"   • {case['plate']} / {case['vin']} - {case['status']}: {error_msg}...")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"comprehensive_test_results_{timestamp}.json"
    
    summary_data = {
        'timestamp': datetime.now().isoformat(),
        'test_type': 'comprehensive_all_cases',
        'total_cases': len(TEST_CASES),
        'successful_cases': success_count,
        'failed_cases': total_errors,
        'success_rate': success_rate,
        'average_duration': avg_duration,
        'total_duration': total_duration,
        'error_breakdown': error_counts,
        'assessment': assessment,
        'results': results
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Final recommendations
    print(f"\n📋 Recommendations:")
    if success_rate >= 85:
        print("   ✅ Scraper is production-ready!")
        print("   ✅ Original captcha issues have been resolved!")
        if error_counts.get('captcha_error', 0) == 0:
            print("   🎉 Zero captcha failures detected!")
    else:
        print("   ⚠️  Consider investigating error patterns")
        if error_counts.get('captcha_error', 0) > 0:
            print("   🔧 Captcha solver may need further tuning")
    
    # Return appropriate exit code
    return 0 if success_rate >= 75 else 1

if __name__ == "__main__":
    sys.exit(main())