"""
Scoring engine for FundFlow Projects (Intelligence Layer V2).
Implements a weighted, deterministic, and explainable framework.
"""
from typing import Dict, Any, Tuple, List
from datetime import datetime
from loguru import logger
from database.models import Project, FundingRound, Investor, RoundType, ProjectStage

def calculate_project_score(project: Project) -> Tuple[float, str]:
    """
    Weighted Deterministic Scoring Framework (FundFlow V2)
    Categories: Network Usage (25%), Economic (20%), Ecosystem (20%), Token (15%), Risk (20%)
    """
    breakdown = {
        "network_usage": {"score": 0, "weight": 0.25},
        "economic_sustainability": {"score": 0, "weight": 0.20},
        "ecosystem_growth": {"score": 0, "weight": 0.20},
        "token_mechanics": {"score": 0, "weight": 0.15},
        "risk_profile": {"score": 0, "weight": 0.20}
    }
    
    # Determine if this is a Startup or Mature project
    is_startup = project.stage in [ProjectStage.CONCEPT, ProjectStage.DEVELOPMENT] or \
                 not project.tvl or \
                 (project.tvl and project.tvl < 1_000_000)

    data_points_found = 0

    if is_startup:
        # === STARTUP LOGIC (40% Funding / 40% Social / 20% Risk) ===
        breakdown = {
            "funding_quality": {"score": 30, "weight": 0.40},
            "social_velocity": {"score": 30, "weight": 0.40},
            "risk_profile": {"score": 100, "weight": 0.20}
        }
        
        # A. Funding Quality
        inv_score = 30
        for r in project.funding_rounds:
            for inv in getattr(r, 'investors', []):
                if inv.tier == 1: inv_score += 25
                elif inv.tier == 2: inv_score += 10
        breakdown["funding_quality"]["score"] = min(100, inv_score)
        
        # B. Social/News Velocity
        social_val = 30
        if project.twitter_followers:
            social_val += min(70, (project.twitter_followers / 5000) * 10)
        # News boost
        ds = project.data_sources or {}
        if ds.get("news_signal") == "High Press Coverage": social_val += 20
        elif ds.get("news_signal") == "Emerging Awareness": social_val += 10
        
        breakdown["social_velocity"]["score"] = min(100, social_val)
        
        # C. Risk (Startup version)
        risk_val = 100
        risk_factors = []
        if not project.website:
            risk_val -= 20
            risk_factors.append("Missing Website")
        breakdown["risk_profile"]["score"] = risk_val
        project.risk_factors = risk_factors
        
        data_points_found = 3

    else:
        # === MATURE LOGIC (25% Usage / 20% Econ / 20% Ecosystem / 15% Token / 20% Risk) ===
        breakdown = {
            "network_usage": {"score": 0, "weight": 0.25},
            "economic_sustainability": {"score": 20, "weight": 0.20},
            "ecosystem_growth": {"score": 40, "weight": 0.20},
            "token_mechanics": {"score": 15, "weight": 0.15},
            "risk_profile": {"score": 100, "weight": 0.20}
        }
        
        # 1. Network Usage
        if project.tvl:
            usage_val = 50
            if project.tvl_30d_change and project.tvl_30d_change > 0:
                usage_val += min(40, project.tvl_30d_change * 2)
            breakdown["network_usage"]["score"] = usage_val
            data_points_found += 1

        # 2. Economic Sustainability
        if project.revenue_24h:
            rev_score = min(100, (project.revenue_24h / 100000) * 100)
            breakdown["economic_sustainability"]["score"] = rev_score
            data_points_found += 1

        # 3. Ecosystem Growth
        inv_score = 40
        for r in project.funding_rounds:
            for inv in getattr(r, 'investors', []):
                if inv.tier == 1: inv_score += 15
                elif inv.tier == 2: inv_score += 5
        breakdown["ecosystem_growth"]["score"] = min(100, inv_score)
        data_points_found += 1

        # 4. Token Mechanics
        if project.has_token:
            breakdown["token_mechanics"]["score"] = 60 if project.token_symbol else 30
            data_points_found += 1

        # 5. Risk Profile
        risk_val = 100
        risk_factors = []
        if project.sector in ["L2", "Rollup"]:
            risk_factors.append("Sequencer Centralization")
            risk_val -= 15
        if not project.website:
            risk_val -= 20
            risk_factors.append("Missing Website")
        breakdown["risk_profile"]["score"] = risk_val
        project.risk_factors = risk_factors
        data_points_found += 1

    # Final Math (Common for both)
    final_score = sum(c["score"] * c["weight"] for c in breakdown.values())
    
    # Coverage mapping
    confidence = (data_points_found / (3 if is_startup else 5)) * 100
    project.data_confidence = confidence
    project.scoring_breakdown = breakdown
    
    # Grade Mapping
    grade = "N/A"
    if confidence >= 40:
        if final_score >= 85: grade = "A+"
        elif final_score >= 70: grade = "A"
        elif final_score >= 55: grade = "B"
        elif final_score >= 40: grade = "C"
        elif final_score >= 25: grade = "D"
        else: grade = "F"
    
    logger.info(f"Scored {project.name}: {final_score:.1f} ({grade})")
    return float(final_score), grade
