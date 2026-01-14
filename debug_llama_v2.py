import requests
import json

def test_defillama():
    slugs = ["uniswap", "optimism"]
    for slug in slugs:
        print(f"--- Testing: {slug} ---")
        # Protocol Test
        url = f"https://api.llama.fi/protocol/{slug.lower()}"
        res = requests.get(url)
        print(f"Protocol API ({url}) status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Protocol TVL: {data.get('tvl')}")
            print(f"Protocol Name: {data.get('name')}")
            print(f"Chains: {data.get('chains')}")
        
        # Chain Test
        url = f"https://api.llama.fi/v2/historicalChainTvl/{slug.capitalize()}"
        res = requests.get(url)
        print(f"Chain API ({url}) status: {res.status_code}")
        if res.status_code == 200:
            try:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"Chain latest TVL: {data[-1]['tvl']}")
                else:
                    print(f"Chain TVL data is empty or not a list: {data}")
            except Exception as e:
                print(f"Error parsing chain data: {e}")
        print("-" * 20)

if __name__ == "__main__":
    test_defillama()
