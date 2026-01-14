import requests
query = "Union Labs"
url = f"https://api.coingecko.com/api/v3/search?query={query}"
res = requests.get(url)
print(res.json())
