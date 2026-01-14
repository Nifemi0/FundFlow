"""
Configuration settings for FundFlow application.
Loads environment variables and provides application-wide settings.
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Telegram Bot
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(..., env="REDIS_URL")
    
    # API Keys
    cryptorank_api_key: str = Field(..., env="CRYPTORANK_API_KEY")
    coingecko_api_key: Optional[str] = Field(None, env="COINGECKO_API_KEY")
    coinmarketcap_api_key: Optional[str] = Field(None, env="COINMARKETCAP_API_KEY")
    twitter_bearer_token: Optional[str] = Field(None, env="TWITTER_BEARER_TOKEN")
    github_token: Optional[str] = Field(None, env="GITHUB_TOKEN")
    newsapi_key: Optional[str] = Field(None, env="NEWSAPI_KEY")
    
    # Application Settings
    environment: str = Field("development", env="ENVIRONMENT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    debug: bool = Field(False, env="DEBUG")
    
    # Rate Limiting
    max_requests_per_minute: int = Field(30, env="MAX_REQUESTS_PER_MINUTE")
    cache_ttl_seconds: int = Field(3600, env="CACHE_TTL_SECONDS")
    
    # Report Generation
    max_report_length: int = Field(4096, env="MAX_REPORT_LENGTH")
    pdf_reports_enabled: bool = Field(True, env="PDF_REPORTS_ENABLED")
    
    # Data Collection
    scraper_run_interval_hours: int = Field(6, env="SCRAPER_RUN_INTERVAL_HOURS")
    historical_data_days: int = Field(730, env="HISTORICAL_DATA_DAYS")
    
    # Alerts & Notifications
    alert_channel_id: Optional[str] = Field(None, env="ALERT_CHANNEL_ID")
    admin_user_ids: List[int] = Field(default_factory=list, env="ADMIN_USER_IDS")
    
    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# API Base URLs
class APIEndpoints:
    """External API endpoints."""
    CRYPTORANK_BASE = "https://api.cryptorank.io/v1"
    COINGECKO_BASE = "https://api.coingecko.com/api/v3"
    COINMARKETCAP_BASE = "https://pro-api.coinmarketcap.com/v1"
    GITHUB_BASE = "https://api.github.com"
    TWITTER_BASE = "https://api.twitter.com/2"
    NEWSAPI_BASE = "https://newsapi.org/v2"


# Grade Thresholds
class GradeThresholds:
    """Project grading thresholds."""
    A_PLUS = 95  # Exceptional (top-tier VCs, strong team, high traction)
    A = 85       # Excellent
    B = 70       # Good
    C = 50       # Average
    D = 30       # Below average
    # Below D threshold = not graded/shown


# Investor Tiers
TOP_TIER_INVESTORS = [
    "paradigm",
    "andreessen horowitz",
    "a16z crypto",
    "coinbase ventures",
    "binance labs",
    "polychain capital",
    "pantera capital",
    "sequoia capital",
    "tiger global",
    "framework ventures",
    "dragonfly capital",
    "electric capital",
    "multicoin capital",
    "variant fund",
    "1kx",
    "blockchain capital",
]

TIER_2_INVESTORS = [
    "animoca brands",
    "jump crypto",
    "galaxy digital",
    "dcg",
    "circle ventures",
    "balaji srinivasan",
    "naval ravikant",
]
