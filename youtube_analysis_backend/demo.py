"""
Quick demo script to test the YouTube Analysis API
"""
import requests
import json
import time

# API endpoint
BASE_URL = "http://localhost:8000"

print("🎬 YouTube Channel Analysis API - Quick Demo")
print("=" * 60)

# Test 1: Health check
print("\n1️⃣ Testing health endpoint...")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test 2: API info
print("\n2️⃣ Getting API info...")
response = requests.get(f"{BASE_URL}/")
print(f"   Status: {response.status_code}")
print(f"   Response: {json.dumps(response.json(), indent=2)}")

# Test 3: Analyze a channel (this will take 10-30 seconds)
print("\n3️⃣ Analyzing a YouTube channel...")
print("   Channel: @mkbhd (Marques Brownlee)")
print("   ⏳ This may take 10-30 seconds for first-time analysis...")

start_time = time.time()

try:
    response = requests.post(
        f"{BASE_URL}/v1/analyze",
        json={"channel_url": "https://youtube.com/@mkbhd"},
        timeout=60  # 60 second timeout
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n   ✅ Analysis completed in {elapsed:.1f} seconds!")
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        
        # Channel info
        channel = result['channel']
        print(f"\n📺 Channel: {channel['title']}")
        print(f"   Subscribers: {channel['subscriber_count']:,}")
        print(f"   Total Videos: {channel['video_count']:,}")
        
        # Analysis
        analysis = result['analysis']
        print(f"\n📝 Summary:")
        print(f"   {analysis['summary'][:200]}...")
        
        print(f"\n🏷️  Themes:")
        for theme in analysis['themes'][:5]:
            print(f"   • {theme}")
        
        print(f"\n👥 Target Audience:")
        print(f"   {analysis['target_audience'][:150]}...")
        
        print(f"\n🎨 Content Style:")
        print(f"   {analysis['content_style'][:150]}...")
        
        print(f"\n📅 Upload Frequency:")
        print(f"   {analysis['upload_frequency']}")
        
        # Metadata
        meta = result['meta']
        print(f"\n📊 Analysis Metadata:")
        print(f"   Videos Analyzed: {meta['videos_analyzed']}")
        print(f"   Total Videos: {meta['total_videos']}")
        print(f"   Confidence: {meta['confidence']:.2%}")
        print(f"   Freshness: {meta['freshness']}")
        print(f"   Model: {meta['model_version']}")
        
        print("\n" + "=" * 60)
        print("✨ Demo completed successfully!")
        
        # Save full result
        with open('demo_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\n💾 Full result saved to: demo_result.json")
        
    else:
        print(f"\n   ❌ Error: {response.status_code}")
        print(f"   Response: {response.json()}")

except requests.exceptions.Timeout:
    print("\n   ⏱️  Request timed out (>60s)")
    print("   This might happen if:")
    print("   - The channel has many videos")
    print("   - Network is slow")
    print("   - YouTube API is slow")
    
except Exception as e:
    print(f"\n   ❌ Error: {e}")

print("\n" + "=" * 60)
print("📚 API Documentation: http://localhost:8000/v1/docs")
print("🔍 Try it yourself in your browser!")
print("=" * 60)
