import requests

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
BASE_URL = "https://api.cryptorank.io/v1/currencies"

params_sets = [
    {"api_key": API_KEY, "limit": 10},
    {"api_key": API_KEY, "limit": 10, "sort": "rank"},
    {"api_key": API_KEY, "limit": 10, "order": "desc"},
]

for p in params_sets:
    print(f"Testing {p}...")
    r = requests.get(BASE_URL, params=p)
    print(f"Status: {r.status_code}")
    if r.status_code == 400:
        print(f"Response: {r.text}")
    else:
        print("Success!")
    print("-" * 20)
