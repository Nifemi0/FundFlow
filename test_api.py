import requests
import os

API_KEY = "d99f87219bb7a5a033a5af8c40a6975b564e9ded9e53e7c435f7b4d4a5e2"
BASE_URL = "https://api.cryptorank.io/v1"

endpoints = [
    "/funding-rounds",
    "/currencies?limit=1", # Should work on all keys
    "/funds/raising",
]

headers = {"api-key": API_KEY}

print(f"Testing with Key: {API_KEY[:5]}...")

for ep in endpoints:
    url = BASE_URL + ep
    print(f"Testing {url}...")
    try:
        r = requests.get(url, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("SUCCESS! Data sample:", str(r.json())[:100])
        else:
            print("Response:", r.text[:200])
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
