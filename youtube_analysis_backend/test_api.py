"""
Simple API Test - Tests the backend without Redis dependency
"""
import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = 'http://localhost:8000'
API_VERSION = 'v1'

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def test_api_health():
    """Test 1: Check if API is running"""
    print_header("TEST 1: API Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is running")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Environment: {data.get('environment')}")
            return True
        else:
            print_error(f"API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is the server running?")
        print_info("Start the server with: python main.py")
        return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_api_root():
    """Test 2: Check root endpoint"""
    print_header("TEST 2: API Root Endpoint")
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Root endpoint accessible")
            print_info(f"Service: {data.get('service')}")
            print_info(f"Version: {data.get('version')}")
            print_info(f"Docs: {API_BASE_URL}{data.get('docs')}")
            return True
        else:
            print_error(f"Root endpoint returned status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Root endpoint test failed: {e}")
        return False

def test_channel_analysis():
    """Test 3: Analyze a channel"""
    print_header("TEST 3: Channel Analysis")
    
    test_url = "https://youtube.com/@mkbhd"
    print_info(f"Testing with: {test_url}")
    print_info("This may take 10-30 seconds for first-time analysis...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/{API_VERSION}/analyze",
            json={"channel_url": test_url},
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print_success(f"Analysis completed in {elapsed:.2f} seconds")
            
            # Display results
            print("\n" + "-" * 70)
            print(f"📺 Channel: {data['channel']['title']}")
            print(f"   Subscribers: {data['channel']['subscriber_count']:,}")
            print(f"   Videos: {data['channel']['video_count']:,}")
            
            print(f"\n📊 Analysis:")
            print(f"   Videos Analyzed: {data['meta']['videos_analyzed']}")
            print(f"   Confidence: {data['meta']['confidence']:.2%}")
            print(f"   Freshness: {data['meta']['freshness']}")
            
            print(f"\n📝 Summary:")
            summary = data['analysis']['summary']
            print(f"   {summary[:200]}...")
            
            print(f"\n🏷️  Themes:")
            for theme in data['analysis']['themes'][:5]:
                print(f"   • {theme}")
            
            print(f"\n👥 Target Audience:")
            print(f"   {data['analysis']['target_audience'][:150]}...")
            
            print(f"\n🎨 Content Style:")
            print(f"   {data['analysis']['content_style'][:150]}...")
            
            print(f"\n📅 Upload Frequency:")
            print(f"   {data['analysis']['upload_frequency']}")
            
            print("-" * 70)
            
            # Save result
            output_file = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print_success(f"Full result saved to: {output_file}")
            
            # Test cache hit
            print_info("\nTesting cache performance (should be instant)...")
            cache_start = time.time()
            
            cache_response = requests.post(
                f"{API_BASE_URL}/{API_VERSION}/analyze",
                json={"channel_url": test_url},
                timeout=10
            )
            
            cache_elapsed = time.time() - cache_start
            
            if cache_response.status_code == 200:
                print_success(f"Cache hit! Response time: {cache_elapsed*1000:.2f}ms")
            
            return True
            
        else:
            error_data = response.json()
            print_error(f"Analysis failed with status code: {response.status_code}")
            print_error(f"Error: {error_data}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out. The analysis is taking too long.")
        return False
    except Exception as e:
        print_error(f"Analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_invalid_url():
    """Test 4: Test with invalid URL"""
    print_header("TEST 4: Invalid URL Handling")
    
    invalid_url = "https://example.com/notayoutubechannel"
    print_info(f"Testing with invalid URL: {invalid_url}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/{API_VERSION}/analyze",
            json={"channel_url": invalid_url},
            timeout=10
        )
        
        if response.status_code == 400:
            print_success("API correctly rejected invalid URL")
            error_data = response.json()
            print_info(f"Error message: {error_data.get('detail', {}).get('error', 'N/A')}")
            return True
        else:
            print_error(f"Expected 400 status code, got: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Invalid URL test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪" * 35)
    print("  YOUTUBE CHANNEL ANALYZER - API TEST SUITE")
    print("🧪" * 35)
    
    tests = [
        ("API Health Check", test_api_health),
        ("API Root Endpoint", test_api_root),
        ("Channel Analysis", test_channel_analysis),
        ("Invalid URL Handling", test_invalid_url)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            # If API is not running, skip remaining tests
            if test_name == "API Health Check" and not result:
                print_error("\n⚠️  API is not running. Skipping remaining tests.")
                print_info("Start the API server with: python main.py")
                break
                
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'=' * 70}")
    print(f"  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"  Status: 🎉 ALL TESTS PASSED!")
    else:
        print(f"  Status: ⚠️  {total - passed} test(s) failed")
    
    print(f"{'=' * 70}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        import sys
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
