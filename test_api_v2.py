import requests

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
BASE_URL = "https://api.cryptorank.io/v1"

# Try different URL structures
endpoints = [
    f"/funding-rounds?api_key={API_KEY}",
    f"/currencies?api_key={API_KEY}&limit=1",
    f"/funds?api_key={API_KEY}",
]

for ep in endpoints:
    url = BASE_URL + ep
    print(f"Testing {url}...")
    try:
        r = requests.get(url)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("SUCCESS")
        else:
            print(f"Failed: {r.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
