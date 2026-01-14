import requests

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
url = f"https://api.cryptorank.io/v1/funding-rounds?api_key={API_KEY}&limit=100"

res = requests.get(url)
if res.status_code == 200:
    rounds = res.json().get("data", [])
    # Search for any project name containing 'drosera'
    matches = [r for r in rounds if "drosera" in r.get("project", {}).get("name", "").lower()]
    for m in matches:
        print(f"Name: {m['project']['name']}, Type: {m['type']}, Amount: {m['amount']}")
else:
    print(f"Error: {res.status_code}")
