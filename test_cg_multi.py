import requests

queries = ["union", "irys", "drosera"]
for query in queries:
    print(f"--- Searching for '{query}' ---")
    url = f"https://api.coingecko.com/api/v3/search?query={query}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        for coin in data.get("coins", []):
            print(f"Name: {coin['name']}, Symbol: {coin['symbol']}, ID: {coin['id']}")
    else:
        print(f"Error: {res.status_code}")
    print("-" * 20)
