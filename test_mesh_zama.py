from scrapers.cryptorank import CryptoRankScraper
from database.queries import get_db
import json

def test_mesh():
    scraper = CryptoRankScraper()
    project = scraper.sync_project_on_demand("Zama")
    if project:
        print(f"Project: {project.name}")
        print(f"Grade: {project.grade_letter}")
        print(f"GitHub Stars: {project.github_stars}")
        print(f"Data Sources: {json.dumps(project.data_sources, indent=2)}")
    else:
        print("Project not found")

if __name__ == "__main__":
    test_mesh()
