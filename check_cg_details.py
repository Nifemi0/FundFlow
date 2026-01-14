import requests
cg_id = "union-2"
url = f"https://api.coingecko.com/api/v3/coins/{cg_id}?localization=false&tickers=false&market_data=false&community_data=false&developer_data=false&sparkline=false"
res = requests.get(url)
data = res.json()
links = data.get('links', {})
print(f"Homepage: {links.get('homepage')}")
print(f"GitHub: {links.get('repos_url', {}).get('github')}")
