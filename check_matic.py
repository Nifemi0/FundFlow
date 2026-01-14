import requests
import json

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
id = 418 # MATIC

url = f"https://api.cryptorank.io/v1/currencies/{id}?api_key={API_KEY}"
r = requests.get(url)
if r.status_code == 200:
    data = r.json()['data']
    print(f"Keys: {data.keys()}")
    for k in ['tokens', 'ico', 'rounds', 'funding']:
        if k in data:
            print(f"{k}: {json.dumps(data[k], indent=2)[:500]}")
else:
    print(f"Error {r.status_code}")
