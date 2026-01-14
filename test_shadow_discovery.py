from scrapers.cryptorank import CryptoRankScraper
from database.queries import get_db, get_project_by_name

def test_shadow_discovery():
    scraper = CryptoRankScraper()
    
    names = ["@ETHGasOfficial (ETHGas)", "@BitRobotNetwork", "@RedotPay"]
    
    for name in names:
        print(f"\n--- Testing Discovery for: {name} ---")
        project = scraper.discover_project(name)
        if project:
            print(f"SUCCESS: Found {project.name}")
            print(f"Grade: {project.grade_letter}")
            ds = project.data_sources or {}
            print(f"News Signal: {ds.get('news_signal')}")
        else:
            print(f"FAILED: Could not discover {name}")

if __name__ == "__main__":
    test_shadow_discovery()
