from scrapers.cryptorank import CryptoRankScraper
from database.queries import get_db, get_project_by_name
import json

def test_discovery():
    scraper = CryptoRankScraper()
    
    targets = ["Zama", "Irys", "Union"]
    for target in targets:
        print(f"--- Discovering {target} ---")
        project = scraper.discover_project(target)
        if project:
            print(f"SUCCESS: Found {project.name}")
            print(f"Description: {project.description[:100] if project.description else 'None'}")
            print(f"Grade: {project.grade_letter}")
        else:
            print(f"FAILED: {target} not found")
        print("-" * 20)

if __name__ == "__main__":
    test_discovery()
