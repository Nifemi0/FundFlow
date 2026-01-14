import requests

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"

url = f"https://api.cryptorank.io/v1/projects?api_key={API_KEY}&limit=5"
print(f"Testing {url}...")
r = requests.get(url)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(f"Keys: {r.json()['data'][0].keys()}")
else:
    print(r.text)
