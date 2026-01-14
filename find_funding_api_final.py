import requests

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"

urls = [
    f"https://api.cryptorank.io/v1/funding-rounds?api_key={API_KEY}",
    f"https://api.cryptorank.io/v1/public/funding-rounds?api_key={API_KEY}",
    f"https://api.cryptorank.io/v1/projects/funding-rounds?api_key={API_KEY}",
    f"https://api.cryptorank.io/v1/ico/funding-rounds?api_key={API_KEY}",
]

for url in urls:
    print(f"Testing {url}...")
    r = requests.get(url)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("Success!")
    print("-" * 20)
