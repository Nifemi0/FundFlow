from scrapers.cryptorank import CryptoRankScraper
from database.queries import get_db, get_project_by_name
import json

def test_uniswap_sync():
    db = get_db()
    scraper = CryptoRankScraper()
    
    # Check if Uniswap exists
    project = get_project_by_name(db, "Uniswap")
    if not project:
        print("Uniswap not found in DB. Creating a placeholder...")
        from database.models import Project
        from utils.helpers import slugify
        project = Project(name="Uniswap", slug=slugify("Uniswap"), token_symbol="UNI")
        db.add(project)
        db.commit()
    
    print(f"Syncing {project.name}...")
    updated_project = scraper.sync_project_on_demand(project.name)
    
    if updated_project:
        print(f"--- Results for {updated_project.name} ---")
        print(f"TVL: {updated_project.tvl}")
        print(f"Revenue: {updated_project.revenue_24h}")
        print(f"Grade: {updated_project.grade_letter}")
        print(f"Score: {updated_project.grade_score}")
        print(f"Breakdown: {json.dumps(updated_project.scoring_breakdown, indent=2)}")
        print(f"Risks: {updated_project.risk_factors}")
    else:
        print("Sync failed!")

if __name__ == "__main__":
    test_uniswap_sync()
