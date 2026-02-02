"""
Direct test of the analysis workflow
"""
from dotenv import load_dotenv
load_dotenv()

from database import init_db, get_db
from analysis_service import AnalysisService

print("=" * 60)
print("TESTING FULL ANALYSIS WORKFLOW")
print("=" * 60)

# Initialize database
init_db()

# Test URL
test_url = "https://youtube.com/@mkbhd"
print(f"\nAnalyzing: {test_url}\n")

# Run analysis
with get_db() as db:
    service = AnalysisService(db)
    result = service.analyze_channel(test_url)

print("\n" + "=" * 60)
if result['success']:
    print("✅ SUCCESS!")
    print(f"Channel: {result['data']['channel']['title']}")
    print(f"Summary: {result['data']['analysis']['summary'][:100]}...")
else:
    print("❌ FAILED!")
    print(f"Error: {result.get('error')}")
    print(f"Code: {result.get('error_code')}")
print("=" * 60)
