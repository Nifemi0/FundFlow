import requests

res = requests.get("https://api.llama.fi/summary/fees/uniswap")
if res.status_code == 200:
    data = res.json()
    print(f"Uniswap 24h Fees: {data.get('total24h')}")
else:
    print(f"Status: {res.status_code}")
