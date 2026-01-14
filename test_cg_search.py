import requests

query = "zama"
url = f"https://api.coingecko.com/api/v3/search?query={query}"
res = requests.get(url)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    for coin in data.get("coins", []):
        print(f"Name: {coin['name']}, Symbol: {coin['symbol']}, ID: {coin['id']}")
else:
    print(res.text)
