import requests

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
res = requests.get(f"https://api.cryptorank.io/v1/currencies?api_key={API_KEY}&limit=100")
if res.status_code == 200:
    coins = res.json()['data']
    for c in coins:
        if c.get('type') == 'ico' or c.get('category') == 'ICO':
            print(f"Found ICO project: {c['name']} (ID: {c['id']})")
    
    # Just pick one that looks interesting (not top 10)
    for c in coins[20:30]:
        print(f"Project: {c['name']} (ID: {c['id']}, Type: {c.get('type')})")
else:
    print(f"Error: {res.status_code}")
