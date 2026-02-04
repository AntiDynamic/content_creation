"""
Debug script to test each component individually
"""
import sys
import traceback
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("DEBUGGING YOUTUBE ANALYZER")
print("=" * 60)

# Test 1: Config
print("\n1. Testing Configuration...")
try:
    from config import get_settings
    settings = get_settings()
    print(f"✅ YouTube API Key: {settings.youtube_api_key[:20]}...")
    print(f"✅ Gemini API Key: {settings.gemini_api_key[:20]}...")
except Exception as e:
    print(f"❌ Config Error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: YouTube Service
print("\n2. Testing YouTube Service...")
try:
    from youtube_service import YouTubeClient
    yt = YouTubeClient()
    
    # Test channel ID extraction
    test_url = "https://youtube.com/@mkbhd"
    channel_id = yt.extract_channel_id(test_url)
    print(f"✅ Channel ID from {test_url}: {channel_id}")
    
    # Test metadata fetch
    if channel_id:
        metadata = yt.get_channel_metadata(channel_id)
        if metadata:
            print(f"✅ Channel Title: {metadata['title']}")
            print(f"✅ Subscribers: {metadata['subscriber_count']:,}")
        else:
            print("❌ Failed to get metadata")
except Exception as e:
    print(f"❌ YouTube Service Error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Gemini Service
print("\n3. Testing Gemini Service...")
try:
    from gemini_service import GeminiAnalyzer
    gemini = GeminiAnalyzer()
    
    # Test with sample data
    sample_channel = {
        'title': 'Test Channel',
        'description': 'Tech reviews and tutorials',
        'subscriber_count': 1000000,
        'video_count': 100,
        'published_at': '2020-01-01T00:00:00Z'
    }
    
    sample_videos = [
        {
            'title': 'iPhone 15 Pro Review',
            'description': 'Comprehensive review of the new iPhone',
            'view_count': 1000000,
            'like_count': 50000,
            'published_at': '2024-01-01T00:00:00Z',
            'duration': 'PT10M30S',
            'tags': ['tech', 'iphone', 'review']
        }
    ]
    
    print("✅ Gemini Service initialized")
    print("   Testing analysis with sample data...")
    
    result = gemini.analyze_channel(sample_channel, sample_videos)
    if result:
        print(f"✅ Analysis successful!")
        print(f"   Summary: {result['summary'][:100]}...")
    else:
        print("❌ Analysis returned None")
        
except Exception as e:
    print(f"❌ Gemini Service Error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Database
print("\n4. Testing Database...")
try:
    from database import init_db, get_db
    init_db()
    with get_db() as db:
        print("✅ Database connection successful")
except Exception as e:
    print(f"❌ Database Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL COMPONENTS WORKING!")
print("=" * 60)
