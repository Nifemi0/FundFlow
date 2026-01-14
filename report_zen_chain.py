from scrapers.cryptorank import CryptoRankScraper
from database.queries import get_db, get_project_by_name
from utils.registry import resolve_entity_name
import json

def report_zen_chain():
    scraper = CryptoRankScraper()
    query = "ZenChain" # Likely the canonical name for @zen_chain
    
    print(f"--- Searching for: {query} ---")
    project = scraper.discover_project(query)
    
    if not project:
        # Fallback to a broader search
        print("Initial discovery failed. Trying broader search...")
        project = scraper.discover_project("Zen Chain")
        
    if project:
        print(f"Project found/imported: {project.name}")
        # Sync to get all mesh data
        project = scraper.sync_project_on_demand(project.name)
        
        print("\n--- INTEL SUMMARY ---")
        print(f"Name: {project.name}")
        print(f"Grade: {project.grade_letter}")
        print(f"Sector: {project.sector}")
        print(f"Website: {project.website}")
        print(f"GitHub: {project.github_url}")
        print(f"GitHub Stars: {project.github_stars}")
        print(f"Data Sources: {json.dumps(project.data_sources, indent=2)}")
        
        ds = project.data_sources or {}
        if ds.get("code_signal"): print(f"👨‍💻 Code: {ds['code_signal']}")
        if ds.get("hiring_signal"): print(f"💼 Hiring: {ds['hiring_signal']}")
        if ds.get("news_signal"): print(f"📰 News: {ds['news_signal']}")
        
    else:
        print("FAILED: ZenChain could not be discovered autonomousy. Performing broad web search...")
        # Since the user gave a handle, it might be very early or renamed.
        
if __name__ == "__main__":
    report_zen_chain()
