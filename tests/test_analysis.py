"""
Simple test script to verify the system works end-to-end
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from database import init_db, get_db
from analysis_service import AnalysisService
import json


def test_analysis():
    """Test the complete analysis workflow"""
    
    print("🧪 YouTube Channel Analysis - Test Script\n")
    
    # Initialize database
    print("1️⃣ Initializing database...")
    init_db()
    print("✅ Database initialized\n")
    
    # Test channel URL (using a popular tech channel)
    test_url = "https://youtube.com/@mkbhd"
    print(f"2️⃣ Testing with channel: {test_url}\n")
    
    # Run analysis
    print("3️⃣ Running analysis...")
    print("   This may take 10-30 seconds for first-time analysis...\n")
    
    with get_db() as db:
        service = AnalysisService(db)
        result = service.analyze_channel(test_url)
    
    # Display results
    if result['success']:
        print("✅ Analysis completed successfully!\n")
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        data = result['data']
        
        # Channel info
        print(f"\n📺 Channel: {data['channel']['title']}")
        print(f"   Subscribers: {data['channel']['subscriber_count']:,}")
        print(f"   Total Videos: {data['channel']['video_count']:,}")
        
        # Analysis
        print(f"\n📊 Analysis:")
        print(f"   Videos Analyzed: {data['meta']['videos_analyzed']}")
        print(f"   Confidence: {data['meta']['confidence']:.2%}")
        print(f"   Freshness: {data['meta']['freshness']}")
        print(f"   Source: {result['source']}")
        
        print(f"\n📝 Summary:")
        print(f"   {data['analysis']['summary'][:200]}...")
        
        print(f"\n🏷️  Themes:")
        for theme in data['analysis']['themes']:
            print(f"   • {theme}")
        
        print(f"\n👥 Target Audience:")
        print(f"   {data['analysis']['target_audience'][:150]}...")
        
        print(f"\n🎨 Content Style:")
        print(f"   {data['analysis']['content_style'][:150]}...")
        
        print(f"\n📅 Upload Frequency:")
        print(f"   {data['analysis']['upload_frequency']}")
        
        print("\n" + "=" * 60)
        
        # Save full result to file
        with open('test_result.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print("\n💾 Full result saved to: test_result.json")
        
        # Test cache hit
        print("\n4️⃣ Testing cache performance...")
        print("   Running same analysis again (should be instant)...\n")
        
        import time
        start = time.time()
        
        with get_db() as db:
            service = AnalysisService(db)
            cached_result = service.analyze_channel(test_url)
        
        elapsed = time.time() - start
        
        if cached_result['success']:
            print(f"✅ Cache hit! Response time: {elapsed*1000:.2f}ms")
            print(f"   Source: {cached_result.get('source', 'unknown')}")
        
        print("\n✨ All tests passed!")
        
    else:
        print("❌ Analysis failed!")
        print(f"   Error: {result.get('error')}")
        print(f"   Code: {result.get('error_code')}")


if __name__ == "__main__":
    try:
        test_analysis()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
