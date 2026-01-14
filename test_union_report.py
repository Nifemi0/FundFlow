from scrapers.cryptorank import CryptoRankScraper
from database.queries import get_db, get_project_by_name
import json

def test_union_intelligence():
    scraper = CryptoRankScraper()
    
    print("--- Phase 1: Deep Discovery (Search: Union) ---")
    # Using 'Union' which is the tracker name
    project = scraper.discover_project("Union")
    
    if project:
        print(f"Project Created: {project.name} (Slug: {project.slug})")
        
        print("--- Phase 2: Mesh Sync ---")
        enriched = scraper.sync_project_on_demand(project.name)
        
        if enriched:
            print(f"Grade: {enriched.grade_letter}")
            print(f"GitHub URL: {enriched.github_url}")
            print(f"GitHub Stars: {enriched.github_stars}")
            print(f"Data Sources: {json.dumps(enriched.data_sources, indent=2)}")
        else:
            print("Sync failed.")
    else:
        print("FAILED: Union could not be discovered.")

if __name__ == "__main__":
    test_union_intelligence()
