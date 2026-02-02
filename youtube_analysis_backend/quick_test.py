import requests
import json

# Test the API
url = "http://localhost:8000/v1/analyze"
data = {"channel_url": "https://youtube.com/@mkbhd"}

print("Testing API endpoint...")
print(f"URL: {url}")
print(f"Data: {data}")
print()

try:
    response = requests.post(url, json=data, timeout=60)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
