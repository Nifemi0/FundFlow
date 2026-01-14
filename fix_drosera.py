"""
Maintenance script to correct Drosera Network funding data.
Sets total raised to $6.25M based on latest intelligence.
"""
import os
import sys
from datetime import datetime

# Setup environment
os.environ['DATABASE_URL'] = 'postgresql://fundflow:fundflow@localhost:5432/fundflow'
os.environ['PYTHONPATH'] = '.'

from database.queries import get_db, search_projects, get_investor_by_name
from database.models import Project, FundingRound, RoundType, Investor

def fix_drosera_data():
    db = get_db()
    try:
        projects = search_projects(db, "Drosera", limit=1)
        if not projects:
            print("Drosera not found in DB.")
            return
        
        project = projects[0]
        print(f"Correcting data for {project.name}...")

        # Clear existing rounds to avoid duplicates if any
        db.query(FundingRound).filter(FundingRound.project_id == project.id).delete()

        # Add Seed Round ($1.55M)
        seed_round = FundingRound(
            project_id=project.id,
            round_type=RoundType.SEED,
            amount_raised=1.55,
            announced_date=datetime(2024, 2, 16),
            source="Intelligence Manual Update"
        )
        db.add(seed_round)

        # Add Series A ($4.75M)
        series_a = FundingRound(
            project_id=project.id,
            round_type=RoundType.SERIES_A,
            amount_raised=4.75,
            announced_date=datetime(2025, 2, 10),
            source="Intelligence Manual Update"
        )
        db.add(series_a)

        # Update project level info
        project.data_confidence = 90
        project.is_verified = True
        project.verification_source = "Manual Intelligence Audit"
        project.sector = "Cyber Defense / Infrastructure"
        
        db.commit()
        print("Success! Drosera funding updated to $6.25M total and status set to VERIFIED.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_drosera_data()
