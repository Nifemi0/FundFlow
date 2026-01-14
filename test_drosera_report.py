from scrapers.cryptorank import CryptoRankScraper
from database.queries import get_db, get_project_by_name
import json

def test_drosera_intelligence():
    scraper = CryptoRankScraper()
    
    print("--- Phase 1: Deep Discovery ---")
    project = scraper.discover_project("Drosera Network")
    if not project:
        print("Discovery failed. Trying direct sync...")
        project = scraper.sync_project_on_demand("Drosera Network")
        
    if project:
        print(f"Project: {project.name}")
        print(f"Grade: {project.grade_letter}")
        print(f"Confidence: {project.data_confidence}%")
        print(f"GitHub URL: {project.github_url}")
        print(f"GitHub Stars: {project.github_stars}")
        print(f"TVL: {project.tvl}")
        print(f"Data Sources: {json.dumps(project.data_sources, indent=2)}")
        print(f"Scoring: {json.dumps(project.scoring_breakdown, indent=2)}")
        
        # Displaying what would be in the PDF
        ds = project.data_sources or {}
        print("\n--- EXECUTIVE SUMMARY SIGNALS ---")
        if ds.get("code_signal"): print(f"👨‍💻 Code: {ds['code_signal']}")
        if ds.get("hiring_signal"): print(f"💼 Hiring: {ds['hiring_signal']}")
        if ds.get("news_signal"): print(f"📰 News: {ds['news_signal']}")
        if ds.get("commit_velocity"): print(f"📈 30D Commits: {ds['commit_velocity']}")
    else:
        print("FAILED: Drosera could not be found.")

if __name__ == "__main__":
    test_drosera_intelligence()
