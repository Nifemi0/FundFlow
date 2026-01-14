from scrapers.cryptorank import CryptoRankScraper
from database.queries import get_db, get_project_by_name
from utils.registry import resolve_entity_name
import json

def test_union_labs_autonomous():
    scraper = CryptoRankScraper()
    
    query = "Union Labs"
    canonical = resolve_entity_name(query)
    print(f"--- Query: {query} -> Resolved: {canonical} ---")
    
    project = scraper.discover_project(canonical)
    
    if project:
        print(f"Project Created/Synced: {project.name}")
        print(f"Grade: {project.grade_letter}")
        print(f"GitHub URL: {project.github_url}")
        print(f"GitHub Stars: {project.github_stars}")
        print(f"Data Sources: {json.dumps(project.data_sources, indent=2)}")
    else:
        print(f"FAILED: {query} could not be discovered.")

if __name__ == "__main__":
    test_union_labs_autonomous()
