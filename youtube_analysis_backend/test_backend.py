"""
Comprehensive Backend Test Suite
Tests all components: YouTube API, Gemini AI, Database, Cache, and API endpoints
"""
import sys
import os
import time
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from database import init_db, get_db
from analysis_service import AnalysisService
from youtube_service import YouTubeService
from gemini_service import GeminiService
from cache import cache


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


def test_environment():
    """Test 1: Verify environment variables"""
    print_header("TEST 1: Environment Configuration")
    
    required_vars = [
        'YOUTUBE_API_KEY',
        'GEMINI_API_KEY'
    ]
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print_success(f"{var} is set ({len(value)} characters)")
        else:
            print_error(f"{var} is NOT set")
            all_present = False
    
    return all_present


def test_database():
    """Test 2: Database initialization"""
    print_header("TEST 2: Database Connection")
    
    try:
        init_db()
        print_success("Database initialized successfully")
        
        with get_db() as db:
            print_success("Database connection established")
        
        return True
    except Exception as e:
        print_error(f"Database test failed: {e}")
        return False


def test_youtube_api():
    """Test 3: YouTube API connectivity"""
    print_header("TEST 3: YouTube API")
    
    try:
        youtube = YouTubeService()
        
        # Test with a known channel
        test_handle = "@mkbhd"
        print_info(f"Testing with channel: {test_handle}")
        
        channel_id = youtube.get_channel_id_from_handle(test_handle)
        if channel_id:
            print_success(f"Channel ID retrieved: {channel_id}")
        else:
            print_error("Failed to retrieve channel ID")
            return False
        
        # Get channel metadata
        metadata = youtube.get_channel_metadata(channel_id)
        if metadata:
            print_success(f"Channel: {metadata['title']}")
            print_info(f"  Subscribers: {metadata['subscriber_count']:,}")
            print_info(f"  Videos: {metadata['video_count']:,}")
        else:
            print_error("Failed to retrieve channel metadata")
            return False
        
        # Get recent videos
        videos = youtube.get_recent_videos(channel_id, max_results=5)
        if videos:
            print_success(f"Retrieved {len(videos)} recent videos")
            for i, video in enumerate(videos[:3], 1):
                print_info(f"  {i}. {video['title'][:50]}...")
        else:
            print_error("Failed to retrieve videos")
            return False
        
        return True
    except Exception as e:
        print_error(f"YouTube API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gemini_api():
    """Test 4: Gemini AI connectivity"""
    print_header("TEST 4: Gemini AI")
    
    try:
        gemini = GeminiService()
        
        # Test with sample video data
        test_videos = [
            {
                'title': 'iPhone 15 Pro Review',
                'description': 'Comprehensive review of the new iPhone',
                'view_count': 1000000,
                'like_count': 50000
            },
            {
                'title': 'Best Tech of 2024',
                'description': 'Top tech products this year',
                'view_count': 800000,
                'like_count': 40000
            }
        ]
        
        print_info("Analyzing sample video data...")
        analysis = gemini.analyze_channel(test_videos, max_videos=2)
        
        if analysis:
            print_success("Gemini analysis completed")
            print_info(f"  Summary: {analysis['summary'][:100]}...")
            print_info(f"  Themes: {', '.join(analysis['themes'][:3])}")
            print_info(f"  Target Audience: {analysis['target_audience'][:80]}...")
        else:
            print_error("Failed to get Gemini analysis")
            return False
        
        return True
    except Exception as e:
        print_error(f"Gemini API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache():
    """Test 5: Cache functionality"""
    print_header("TEST 5: Cache System")
    
    try:
        # Test cache set/get
        test_key = "test_channel_123"
        test_data = {
            "channel": {"title": "Test Channel"},
            "analysis": {"summary": "Test summary"}
        }
        
        # Set cache
        cache.set_channel_analysis(test_key, test_data)
        print_success("Cache write successful")
        
        # Get cache
        cached_data = cache.get_channel_analysis(test_key)
        if cached_data and cached_data['channel']['title'] == "Test Channel":
            print_success("Cache read successful")
        else:
            print_error("Cache read failed")
            return False
        
        # Clear cache
        cache.clear()
        print_success("Cache cleared")
        
        return True
    except Exception as e:
        print_error(f"Cache test failed: {e}")
        return False


def test_full_analysis():
    """Test 6: Complete end-to-end analysis"""
    print_header("TEST 6: Full Channel Analysis")
    
    try:
        test_url = "https://youtube.com/@mkbhd"
        print_info(f"Analyzing: {test_url}")
        print_info("This may take 10-30 seconds for first-time analysis...")
        
        start_time = time.time()
        
        with get_db() as db:
            service = AnalysisService(db)
            result = service.analyze_channel(test_url)
        
        elapsed = time.time() - start_time
        
        if result['success']:
            print_success(f"Analysis completed in {elapsed:.2f} seconds")
            
            data = result['data']
            
            # Display results
            print("\n" + "-" * 70)
            print(f"📺 Channel: {data['channel']['title']}")
            print(f"   Subscribers: {data['channel']['subscriber_count']:,}")
            print(f"   Videos: {data['channel']['video_count']:,}")
            print(f"\n📊 Analysis Metadata:")
            print(f"   Videos Analyzed: {data['meta']['videos_analyzed']}")
            print(f"   Confidence: {data['meta']['confidence']:.2%}")
            print(f"   Freshness: {data['meta']['freshness']}")
            print(f"   Source: {result.get('source', 'N/A')}")
            print(f"\n📝 Summary:")
            print(f"   {data['analysis']['summary'][:200]}...")
            print(f"\n🏷️  Themes: {', '.join(data['analysis']['themes'][:5])}")
            print("-" * 70)
            
            # Save result
            output_file = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print_success(f"Full result saved to: {output_file}")
            
            # Test cache hit
            print_info("\nTesting cache performance (should be instant)...")
            cache_start = time.time()
            
            with get_db() as db:
                service = AnalysisService(db)
                cached_result = service.analyze_channel(test_url)
            
            cache_elapsed = time.time() - cache_start
            
            if cached_result['success']:
                print_success(f"Cache hit! Response time: {cache_elapsed*1000:.2f}ms")
                print_info(f"Source: {cached_result.get('source', 'unknown')}")
            
            return True
        else:
            print_error(f"Analysis failed: {result.get('error')}")
            print_error(f"Error code: {result.get('error_code')}")
            return False
            
    except Exception as e:
        print_error(f"Full analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪" * 35)
    print("  YOUTUBE CHANNEL ANALYSIS - COMPREHENSIVE TEST SUITE")
    print("🧪" * 35)
    
    tests = [
        ("Environment Configuration", test_environment),
        ("Database Connection", test_database),
        ("YouTube API", test_youtube_api),
        ("Gemini AI", test_gemini_api),
        ("Cache System", test_cache),
        ("Full Analysis", test_full_analysis)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
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
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
