"""
Database query functions for FundFlow.
Provides high-level query interface for common operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, desc, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session
from database.models import (
    Base, Project, FundingRound, Investor, TeamMember,
    Tag, UserAlert, ScraperRun, RoundType, ProjectStage
)
from config.settings import settings


# Database engine and session
engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Session will be closed by caller


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


# ============================================================================
# PROJECT QUERIES
# ============================================================================

def get_project_by_name(db: Session, name: str) -> Optional[Project]:
    """Get project by  name (case-insensitive)."""
    return db.query(Project).filter(
        func.lower(Project.name) == name.lower()
    ).first()


def get_project_by_slug(db: Session, slug: str) -> Optional[Project]:
    """Get project by slug."""
    return db.query(Project).filter(Project.slug == slug).first()


def search_projects(
    db: Session,
    query: str,
    sector: Optional[str] = None,
    limit: int = 10
) -> List[Project]:
    """Search projects by name, description, website, or social handle."""
    clean_query = query.lower().replace("@", "").removeprefix("https://").removeprefix("http://").removesuffix("/")
    
    filters = [
        or_(
            Project.name.ilike(f"%{query}%"),
            Project.description.ilike(f"%{query}%"),
            Project.website.ilike(f"%{clean_query}%"),
            Project.twitter_handle.ilike(f"%{clean_query}%")
        )
    ]
    
    if sector:
        filters.append(Project.sector == sector)
    
    return db.query(Project).filter(and_(*filters)).limit(limit).all()


def get_recent_funded_projects(
    db: Session,
    days: int = 7,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Get recently funded projects."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        Project, FundingRound
    ).join(
        FundingRound
    ).filter(
        FundingRound.announced_date >= cutoff_date
    ).order_by(
        desc(FundingRound.announced_date)
    ).limit(limit).all()
    
    return [
        {
            "project": project,
            "funding_round": funding_round
        }
        for project, funding_round in results
    ]


def get_project_full_info(db: Session, project_id: int) -> Optional[Dict[str, Any]]:
    """Get complete project information including all relationships."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return None
    
    return {
        "project": project,
        "funding_rounds": project.funding_rounds,
        "team_members": project.team_members,
        "tags": project.tags,
        "total_raised": sum(fr.amount_raised or 0 for fr in project.funding_rounds),
        "latest_round": max(project.funding_rounds, key=lambda x: x.announced_date) if project.funding_rounds else None
    }


# ============================================================================
# FUNDING ROUND QUERIES
# ============================================================================

def get_funding_rounds_by_date_range(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    round_type: Optional[RoundType] = None,
    min_amount: Optional[float] = None
) -> List[FundingRound]:
    """Get funding rounds within date range with optional filters."""
    filters = [
        FundingRound.announced_date >= start_date,
        FundingRound.announced_date <= end_date
    ]
    
    if round_type:
        filters.append(FundingRound.round_type == round_type)
    
    if min_amount:
        filters.append(FundingRound.amount_raised >= min_amount)
    
    return db.query(FundingRound).filter(
        and_(*filters)
    ).order_by(desc(FundingRound.announced_date)).all()


def get_largest_rounds(db: Session, limit: int = 10, days: Optional[int] = None) -> List[FundingRound]:
    """Get largest funding rounds, optionally within recent days."""
    query = db.query(FundingRound).filter(FundingRound.amount_raised.isnot(None))
    
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(FundingRound.announced_date >= cutoff)
    
    return query.order_by(desc(FundingRound.amount_raised)).limit(limit).all()


# ============================================================================
# INVESTOR QUERIES
# ============================================================================

def get_investor_by_name(db: Session, name: str) -> Optional[Investor]:
    """Get investor by name (case-insensitive)."""
    return db.query(Investor).filter(
        func.lower(Investor.name) == name.lower()
    ).first()


def get_investor_portfolio(
    db: Session,
    investor_id: int,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Get all investments by an investor."""
    query = db.query(
        FundingRound, Project
    ).join(
        FundingRound.investors
    ).join(
        FundingRound.project
    ).filter(
        Investor.id == investor_id
    ).order_by(
        desc(FundingRound.announced_date)
    )
    
    if limit:
        query = query.limit(limit)
    
    results = query.all()
    
    return [
        {
            "funding_round": funding_round,
            "project": project
        }
        for funding_round, project in results
    ]


def get_top_investors(db: Session, limit: int = 20) -> List[Investor]:
    """Get most active investors by investment count."""
    return db.query(Investor).order_by(
        desc(Investor.total_investments)
    ).limit(limit).all()


# ============================================================================
# USER ALERT QUERIES
# ============================================================================

def create_alert(
    db: Session,
    telegram_user_id: int,
    project_id: Optional[int] = None,
    investor_id: Optional[int] = None,
    alert_type: str = "new_funding"
) -> UserAlert:
    """Create a new user alert."""
    alert = UserAlert(
        telegram_user_id=telegram_user_id,
        project_id=project_id,
        investor_id=investor_id,
        alert_type=alert_type
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_user_alerts(db: Session, telegram_user_id: int, active_only: bool = True) -> List[UserAlert]:
    """Get all alerts for a user."""
    query = db.query(UserAlert).filter(UserAlert.telegram_user_id == telegram_user_id)
    
    if active_only:
        query = query.filter(UserAlert.is_active == True)
    
    return query.all()


def deactivate_alert(db: Session, alert_id: int, telegram_user_id: int) -> bool:
    """Deactivate a user alert."""
    alert = db.query(UserAlert).filter(
        and_(
            UserAlert.id == alert_id,
            UserAlert.telegram_user_id == telegram_user_id
        )
    ).first()
    
    if alert:
        alert.is_active = False
        db.commit()
        return True
    return False


# ============================================================================
# STATISTICS QUERIES
# ============================================================================

def get_funding_stats(db: Session, days: int = 30) -> Dict[str, Any]:
    """Get funding statistics for a time period."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    rounds = db.query(FundingRound).filter(
        FundingRound.announced_date >= cutoff
    ).all()
    
    total_raised = sum(r.amount_raised or 0 for r in rounds)
    avg_round_size = total_raised / len(rounds) if rounds else 0
    
    # Group by round type
    by_type = {}
    for round_type in RoundType:
        type_rounds = [r for r in rounds if r.round_type == round_type]
        by_type[round_type.value] = {
            "count": len(type_rounds),
            "total": sum(r.amount_raised or 0 for r in type_rounds)
        }
    
    return {
        "period_days": days,
        "total_rounds": len(rounds),
        "total_raised": total_raised,
        "avg_round_size": avg_round_size,
        "by_round_type": by_type,
        "largest_round": max(rounds, key=lambda x: x.amount_raised or 0) if rounds else None
    }


def get_sector_breakdown(db: Session, days: Optional[int] = None) -> Dict[str, int]:
    """Get project count by sector."""
    query = db.query(
        Project.sector,
        func.count(Project.id).label('count')
    )
    
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.join(FundingRound).filter(
            FundingRound.announced_date >= cutoff
        )
    
    query = query.group_by(Project.sector).order_by(desc('count'))
    
    return {sector: count for sector, count in query.all()}


# ============================================================================
# SCRAPER TRACKING
# ============================================================================

def log_scraper_run(
    db: Session,
    scraper_name: str,
    status: str,
    items_collected: int = 0,
    items_new: int = 0,
    items_updated: int = 0,
    errors: Optional[List[str]] = None
) -> ScraperRun:
    """Log a scraper execution."""
    run = ScraperRun(
        scraper_name=scraper_name,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        status=status,
        items_collected=items_collected,
        items_new=items_new,
        items_updated=items_updated,
        errors=errors or []
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
