import requests
import json

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
# Let's try a project known to have had an ICO/IDO
# Search for something like SOL or ADA or something
res = requests.get(f"https://api.cryptorank.io/v1/currencies?api_key={API_KEY}&limit=50")
if res.status_code == 200:
    coins = res.json()['data']
    target = None
    for c in coins:
        if c['symbol'] in ['SOL', 'MATIC', 'AVAX', 'DOT']:
            target = c
            break
    if not target: target = coins[0]
    
    cur_id = target['id']
    print(f"Fetching details for {target['name']} (ID: {cur_id})...")
    
    details_res = requests.get(f"https://api.cryptorank.io/v1/currencies/{cur_id}?api_key={API_KEY}")
    if details_res.status_code == 200:
        data = details_res.json()['data']
        # Print keys to see where rounds might be
        print(f"Keys: {data.keys()}")
        if 'tokens' in data:
            print(f"Tokens: {json.dumps(data['tokens'], indent=2)[:500]}")
        if 'ico' in data:
            print(f"ICO: {json.dumps(data['ico'], indent=2)[:500]}")
    else:
        print(f"Failed to fetch details: {details_res.status_code}")
else:
    print(f"Failed to fetch currencies: {res.status_code}")
