import requests
import json

def test_defillama():
    slugs = ["uniswap", "optimism"]
    for slug in slugs:
        print(f"Testing protocol: {slug}")
        url = f"https://api.llama.fi/protocol/{slug}"
        res = requests.get(url)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Found TVL: {data.get('tvl')}")
        
        print(f"Testing chain: {slug}")
        url = f"https://api.llama.fi/v2/historicalChainTvl/{slug.capitalize()}"
        res = requests.get(url)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            if data:
                print(f"Found latest TVL: {data[-1]['tvl']}")
        print("-" * 20)

if __name__ == "__main__":
    test_defillama()
