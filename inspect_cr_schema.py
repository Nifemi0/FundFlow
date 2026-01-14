import requests
import json

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
# ETH or BTC ID
# Let's try fetching the first currency to get a valid ID
res = requests.get(f"https://api.cryptorank.io/v1/currencies?api_key={API_KEY}&limit=1")
if res.status_code == 200:
    cur = res.json()['data'][0]
    cur_id = cur['id']
    print(f"Fetching details for {cur['name']} (ID: {cur_id})...")
    
    details_res = requests.get(f"https://api.cryptorank.io/v1/currencies/{cur_id}?api_key={API_KEY}")
    if details_res.status_code == 200:
        print(json.dumps(details_res.json(), indent=2)[:2000])
    else:
        print(f"Failed to fetch details: {details_res.status_code}")
else:
    print(f"Failed to fetch currencies: {res.status_code}")
