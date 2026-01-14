import requests

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
BASE_URL = "https://api.cryptorank.io/v1/currencies"

params_sets = [
    {"api_key": API_KEY, "name": "Zama"},
    {"api_key": API_KEY, "symbol": "ZAMA"},
    {"api_key": API_KEY, "slug": "zama"},
    {"api_key": API_KEY, "q": "zama"},
    {"api_key": API_KEY, "search": "zama"},
    {"api_key": API_KEY, "ids": "23857"}, # Check if IDs filter works (numeric)
]

for p in params_sets:
    print(f"Testing {p}...")
    r = requests.get(BASE_URL, params=p)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json().get("data", [])
        if data:
            print(f"Found {len(data)} items. First: {data[0]['name']} ({data[0].get('symbol')})")
        else:
            print("No data found.")
    else:
        print(f"Response: {r.text}")
    print("-" * 20)
