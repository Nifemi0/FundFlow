"""
Database models for FundFlow.
Defines the schema for projects, funding rounds, investors, and related entities.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean,
    ForeignKey, Table, Enum as SQLEnum, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum


Base = declarative_base()


# Association tables for many-to-many relationships
funding_round_investors = Table(
    'funding_round_investors',
    Base.metadata,
    Column('funding_round_id', Integer, ForeignKey('funding_rounds.id')),
    Column('investor_id', Integer, ForeignKey('investors.id'))
)

project_tags = Table(
    'project_tags',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class RoundType(enum.Enum):
    """Funding round types."""
    SEED = "seed"
    PRIVATE = "private"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    STRATEGIC = "strategic"
    TOKEN_SALE = "token_sale"
    IDO = "ido"
    ICO = "ico"
    GRANT = "grant"
    OTHER = "other"


class ProjectStage(enum.Enum):
    """Project development stage."""
    CONCEPT = "concept"
    DEVELOPMENT = "development"
    TESTNET = "testnet"
    MAINNET = "mainnet"
    LAUNCHED = "launched"
    DEPRECATED = "deprecated"


class Project(Base):
    """Main project model."""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    slug = Column(String(255), unique=True, index=True)
    description = Column(Text)
    website = Column(String(500))
    
    # Categorization
    sector = Column(String(100), index=True)  # DeFi, Infrastructure, Gaming, etc.
    category = Column(String(100))  # More specific: DEX, Lending, L2, etc.
    stage = Column(SQLEnum(ProjectStage), index=True)
    
    # Social & Links
    twitter_handle = Column(String(100))
    twitter_followers = Column(Integer)
    github_url = Column(String(500))
    discord_url = Column(String(500))
    telegram_url = Column(String(500))
    
    # Token Info (if applicable)
    has_token = Column(Boolean, default=False)
    token_symbol = Column(String(20))
    token_address = Column(String(100))
    coingecko_id = Column(String(100))
    coinmarketcap_id = Column(String(100))
    
    # Metrics
    github_stars = Column(Integer)
    github_forks = Column(Integer)
    github_contributors = Column(Integer)
    last_commit_date = Column(DateTime)
    
    # Metadata
    founded_date = Column(DateTime)
    country = Column(String(100))
    team_size = Column(Integer)
    
    # Infrastructure & Protocol Metrics (Intelligence V2)
    tvl = Column(Float)
    tvl_30d_change = Column(Float) # Percentage
    dau = Column(Integer) # Daily Active Users
    daily_tx = Column(Integer)
    revenue_24h = Column(Float) # Protocol Revenue
    
    # Grading & Methodology (Explained)
    grade_score = Column(Float)  # 0-100
    grade_letter = Column(String(5))  # A+, A, B, etc.
    data_confidence = Column(Float, default=0) # 0-100 coverage
    is_verified = Column(Boolean, default=False) # Confirmed by high-trust source
    verification_source = Column(String(100)) # Source that verified the project
    scoring_breakdown = Column(JSON) # Store section scores
    risk_factors = Column(JSON) # Explicitly listed risks
    last_graded = Column(DateTime)
    
    # Tracking
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_sources = Column(JSON)  # Sources: CryptoRank, DefiLlama, L2Beat
    
    # Relationships
    funding_rounds = relationship("FundingRound", back_populates="project", cascade="all, delete-orphan")
    team_members = relationship("TeamMember", back_populates="project", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=project_tags, back_populates="projects")
    
    def __repr__(self):
        return f"<Project {self.name} ({self.slug})>"


class FundingRound(Base):
    """Funding round model."""
    __tablename__ = 'funding_rounds'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    
    # Round Details
    round_type = Column(SQLEnum(RoundType), nullable=False, index=True)
    amount_raised = Column(Float)  # In USD
    valuation = Column(Float)  # Pre or post-money valuation in USD
    valuation_type = Column(String(20))  # "pre" or "post"
    
    # Dates
    announced_date = Column(DateTime, nullable=False, index=True)
    closed_date = Column(DateTime)
    
    # Lead Investor
    lead_investor_id = Column(Integer, ForeignKey('investors.id'))
    
    # Other Details
    announcement_url = Column(String(500))
    source = Column(String(100))  # CryptoRank, CoinDesk, etc.
    notes = Column(Text)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="funding_rounds")
    investors = relationship("Investor", secondary=funding_round_investors, back_populates="funding_rounds")
    lead_investor = relationship("Investor", foreign_keys=[lead_investor_id])
    
    def __repr__(self):
        return f"<FundingRound {self.project.name} - {self.round_type.value} ${self.amount_raised}M>"


class Investor(Base):
    """Investor/VC firm model."""
    __tablename__ = 'investors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    slug = Column(String(255), unique=True, index=True)
    
    # Details
    type = Column(String(50))  # VC, Angel, Corporate, etc.
    description = Column(Text)
    website = Column(String(500))
    tier = Column(Integer)  # 1 = top tier, 2 = tier 2, etc.
    
    # Location
    headquarters = Column(String(100))
    country = Column(String(100))
    
    # Social
    twitter_handle = Column(String(100))
    
    # Metrics
    total_investments = Column(Integer, default=0)
    successful_exits = Column(Integer, default=0)
    avg_check_size = Column(Float)
    
    # Tracking
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    funding_rounds = relationship("FundingRound", secondary=funding_round_investors, back_populates="investors")
    
    def __repr__(self):
        return f"<Investor {self.name}>"


class TeamMember(Base):
    """Project team member model."""
    __tablename__ = 'team_members'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # Personal Info
    name = Column(String(255), nullable=False)
    role = Column(String(100))  # Founder, CEO, CTO, etc.
    
    # Background
    bio = Column(Text)
    previous_companies = Column(JSON)  # Array of previous companies
    education = Column(String(255))
    
    # Social
    twitter_handle = Column(String(100))
    linkedin_url = Column(String(500))
    github_handle = Column(String(100))
    
    # Tracking
    joined_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="team_members")
    
    def __repr__(self):
        return f"<TeamMember {self.name} - {self.role}>"


class Tag(Base):
    """Tags for categorizing projects."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50))  # sector, technology, theme, etc.
    
    # Relationships
    projects = relationship("Project", secondary=project_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag {self.name}>"


class UserAlert(Base):
    """User-set alerts for projects or investors."""
    __tablename__ = 'user_alerts'
    
    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(Integer, nullable=False, index=True)
    
    # Alert Target
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    investor_id = Column(Integer, ForeignKey('investors.id'), nullable=True)
    
    # Alert Settings
    alert_type = Column(String(50))  # new_funding, new_investor, price_change, etc.
    is_active = Column(Boolean, default=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime)
    
    def __repr__(self):
        return f"<UserAlert user:{self.telegram_user_id}>"


class ScraperRun(Base):
    """Track scraper execution for monitoring."""
    __tablename__ = 'scraper_runs'
    
    id = Column(Integer, primary_key=True)
    scraper_name = Column(String(100), nullable=False, index=True)
    
    # Execution Details
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    status = Column(String(20))  # success, failed, running
    
    # Results
    items_collected = Column(Integer)
    items_new = Column(Integer)
    items_updated = Column(Integer)
    errors = Column(JSON)
    
    def __repr__(self):
        return f"<ScraperRun {self.scraper_name} - {self.status}>"
