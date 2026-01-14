"""
Unified runner for all data scrapers.
Orchestrates the execution of CryptoRank, Twitter, and future scrapers.
"""
from loguru import logger
import time

from scrapers.cryptorank import run_cryptorank_scraper
from scrapers.twitter import run_twitter_enrichment
from config.settings import settings

def run_all_scrapers(full_history: bool = False):
    """
    Run the complete data collection pipeline.
    
    Args:
        full_history: If True, fetch long history (initial setup)
    """
    logger.info("🚀 Starting FundFlow Data Pipeline")
    
    # 1. Base Data: Funding Rounds & Projects (CryptoRank)
    days = 730 if full_history else 7
    logger.info(f"Step 1: Fetching core data (History: {days} days)...")
    cr_result = run_cryptorank_scraper(days=days)
    
    if cr_result.get("status") != "success":
        logger.error("Core data fetch failed. Aborting pipeline.")
        return
        
    logger.info("✅ Core data updated.")
    
    # 2. Enrichment: Twitter Stats
    # Only run if we actually have a token
    if settings.twitter_bearer_token:
        logger.info("Step 2: Enriching social metrics via Twitter API...")
        # We limit to 50 per run to respect generic rate limits during MVP
        run_twitter_enrichment(limit=50) 
        logger.info("✅ Social metrics updated.")
    else:
        logger.info("ℹ️ Skipping Twitter enrichment (No API Token)")

    # 3. Future: GitHub scraper, News scraper, etc.
    
    logger.success("🎉 Data Pipeline Complete. Database is fresh.")

if __name__ == "__main__":
    run_all_scrapers()
