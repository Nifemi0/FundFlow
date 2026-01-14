import requests

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
BASE_URL = "https://api.cryptorank.io/v1/currencies"

# Since CryptoRank doesn't support 'q', we fetch the first 1000 and filter
print("Fetching 1000 currencies from CryptoRank...")
r = requests.get(BASE_URL, params={"api_key": API_KEY, "limit": 1000})
if r.status_code == 200:
    data = r.json().get("data", [])
    matches = [c for c in data if "drosera" in c['name'].lower() or "drosera" in c['symbol'].lower()]
    for m in matches:
        print(f"Match: {m['name']} ({m['symbol']}), ID: {m['id']}")
else:
    print(f"Error: {r.status_code}")
