import requests
import json

def find_slugs():
    res = requests.get("https://api.llama.fi/protocols")
    if res.status_code == 200:
        protocols = res.json()
        targets = ["Uniswap", "Aave", "Optimism"]
        for p in protocols:
            if any(t.lower() in p['name'].lower() for t in targets):
                print(f"Name: {p['name']}, Slug: {p['slug']}, TVL: {p.get('tvl')}")
    else:
        print(f"Error: {res.status_code}")

if __name__ == "__main__":
    find_slugs()
