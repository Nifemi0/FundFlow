import requests
query = "Union"
url = f"https://api.coingecko.com/api/v3/search?query={query}"
res = requests.get(url)
data = res.json()
for coin in data.get('coins', [])[:5]:
    print(f"{coin['name']} ({coin['symbol']}): {coin['id']}")
