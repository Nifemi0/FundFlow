"""
Initialization script for FundFlow.
Sets up database, runs initial scraper, etc.
"""
import sys
from loguru import logger

from database.queries import init_db, get_db
from config.settings import settings


def setup_database():
    """Initialize database tables."""
    logger.info("Setting up database...")
    try:
        init_db()
        logger.success("✅ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def verify_connections():
    """Verify database and API connections."""
    logger.info("Verifying connections...")
    
    # Check database
    try:
        from sqlalchemy import text
        db = get_db()
        db.execute(text("SELECT 1"))
        db.close()
        logger.success("✅ Database connection OK")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
    
    # Check API keys
    if not settings.telegram_bot_token:
        logger.warning("⚠️  Telegram bot token not set")
    if not settings.cryptorank_api_key:
        logger.warning("⚠️  CryptoRank API key not set")
    
    return True


def run_initial_scrape():
    """Run initial data collection."""
    logger.info("Running initial data scrape...")
    
    try:
        from scrapers.cryptorank import run_cryptorank_scraper
        
        result = run_cryptorank_scraper(days=30)
        
        if result["status"] == "success":
            logger.success(f"✅ Initial scrape completed: {result.get('items_collected', 0)} items")
            return True
        else:
            logger.warning(f"⚠️  Scrape completed with warnings: {result}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Initial scrape failed: {e}")
        return False


def main():
    """Main initialization routine."""
    logger.info("🚀 Starting FundFlow initialization...")
    
    # Step 1: Setup database
    if not setup_database():
        logger.error("Initialization failed at database setup")
        sys.exit(1)
    
    # Step 2: Verify connections
    if not verify_connections():
        logger.error("Initialization failed at connection verification")
        sys.exit(1)
    
    # Step 3: Run initial scrape (optional)
    if "--no-input" in sys.argv:
        response = "y"
        logger.info("Running in no-input mode, proceeding with scrape...")
    else:
        response = input("\n📊 Run initial data scrape (30 days)? This requires a CryptoRank API key. [y/N]: ")
    
    if response.lower() in ['y', 'yes']:
        if not settings.cryptorank_api_key or settings.cryptorank_api_key == "your_cryptorank_api_key":
            logger.warning("⚠️  CryptoRank API key not configured. Skipping scrape.")
        else:
            run_initial_scrape()
    
    logger.success("\n✅ FundFlow initialization complete!")
    logger.info("\nNext steps:")
    logger.info("1. Configure your .env file in config/.env")
    logger.info("2. Get a Telegram bot token from @BotFather")
    logger.info("3. Run: python bot/main.py")
    logger.info("\nFor help, see README.md")


if __name__ == "__main__":
    main()
