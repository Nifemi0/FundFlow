import requests

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
# Search for Optimism to get ID
res = requests.get(f"https://api.cryptorank.io/v1/currencies?api_key={API_KEY}&limit=100")
id = None
if res.status_code == 200:
    for c in res.json()['data']:
        if c['name'].lower() == 'optimism':
            id = c['id']
            break
if not id: id = 1234 # Fallback

endpoints = [
    f"https://api.cryptorank.io/v1/funding-rounds?api_key={API_KEY}",
    f"https://api.cryptorank.io/v1/ico/rounds?api_key={API_KEY}",
    f"https://api.cryptorank.io/v1/currencies/{id}/funding-rounds?api_key={API_KEY}",
]

for url in endpoints:
    print(f"Testing {url}...")
    r = requests.get(url)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("Success!")
    print("-" * 20)
