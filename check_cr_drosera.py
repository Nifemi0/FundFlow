import requests
API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
url = f"https://api.cryptorank.io/v1/currencies?api_key={API_KEY}&limit=500" # Increase limit
res = requests.get(url)
if res.status_code == 200:
    data = res.json().get("data", [])
    matches = [c for c in data if "drosera" in c['name'].lower()]
    print(f"Matches: {matches}")
else:
    print(f"Error {res.status_code}")
