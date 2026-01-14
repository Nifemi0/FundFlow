import sys
import os
from loguru import logger
from config.settings import settings

def setup_app_logger(service_name: str = "fundflow"):
    """
    Sets up a specialized, persistent logging system for FundFlow.
    Features:
    - Console output with clean formatting
    - Persistent file logging with daily rotation
    - Dedicated 'Intelligence' log for discovery signals
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Remove existing handlers to avoid duplicates
    logger.remove()
    
    # 1. Console Handler: Clean, human-readable output
    logger.add(
        sys.stderr, 
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level
    )
    
    # 2. File Handler: Persistent forensic record
    logger.add(
        f"logs/{service_name}_{{time:YYYY-MM-DD}}.log",
        rotation="1 day",
        retention="30 days",
        level=settings.log_level,
        compression="zip",
        enqueue=True
    )
    
    # 3. Specialized Intelligence Sink: Logs actual discovery signals for future LLM training/tuning
    logger.add(
        "logs/intelligence_signals.log",
        filter=lambda record: "SIGNAL" in record["message"],
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        rotation="10 MB",
        retention="1 year",
        enqueue=True
    )
    
    logger.info(f"Logging initialized for {service_name}. Level: {settings.log_level}")
    return logger
