import requests
import json
from scrapers.cryptorank import CryptoRankScraper

scraper = CryptoRankScraper()
# Test enrichment for Hyperliquid
print("Testing CoinGecko enrichment for Hyperliquid...")
details = scraper._fetch_coingecko_details("Hyperliquid")
if details:
    print(f"Success! Name: {details['name']}")
    print(f"Socials: {details['links']['twitter_screen_name']}")
    print(f"Description: {details['description']['en'][:100]}...")
else:
    print("Failed to fetch CoinGecko details.")
