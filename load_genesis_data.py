"""
Genesis data loader for FundFlow.
Populates the database with high-quality 'Smart Money' projects
to ensure the bot has immediate value even before the first scrape.
"""
from datetime import datetime, timedelta
from loguru import logger
from database.queries import get_db, create_project, get_project_by_name
from database.models import Project, FundingRound, Investor, RoundType, ProjectStage
from utils.scoring import calculate_project_score

def load_genesis_data():
    db = get_db()
    
    # 1. Define Tier 1 Investors
    investors_data = [
        {"name": "Paradigm", "tier": 1},
        {"name": "a16z Crypto", "tier": 1},
        {"name": "Polychain Capital", "tier": 1},
        {"name": "Sequoia Capital", "tier": 1},
        {"name": "Dragonfly Capital", "tier": 1},
        {"name": "Coinbase Ventures", "tier": 1},
        {"name": "Binance Labs", "tier": 1},
        {"name": "Pantera Capital", "tier": 1},
    ]
    
    investor_objs = {}
    for inv in investors_data:
        from utils.helpers import slugify
        existing = db.query(Investor).filter(Investor.name == inv["name"]).first()
        if not existing:
            investor = Investor(
                name=inv["name"],
                slug=slugify(inv["name"]),
                tier=inv["tier"]
            )
            db.add(investor)
            db.flush()
            investor_objs[inv["name"]] = investor
        else:
            investor_objs[inv["name"]] = existing

    # 2. Define Genesis Projects
    projects = [
        {
            "name": "Optimism",
            "sector": "Infrastructure",
            "category": "L2",
            "description": "Optimism is a low-cost and lightning-fast Ethereum L2 blockchain.",
            "rounds": [
                {"type": RoundType.SERIES_B, "amount": 150, "lead": "Paradigm", "date": datetime(2022, 3, 17)},
                {"type": RoundType.SERIES_A, "amount": 25, "lead": "a16z Crypto", "date": datetime(2021, 2, 24)}
            ]
        },
        {
            "name": "Uniswap",
            "sector": "DeFi",
            "category": "DEX",
            "description": "Uniswap is the largest decentralized exchange on Ethereum.",
            "rounds": [
                {"type": RoundType.SERIES_C, "amount": 165, "lead": "Polychain Capital", "date": datetime(2022, 10, 13)},
                {"type": RoundType.SERIES_A, "amount": 11, "lead": "a16z Crypto", "date": datetime(2020, 8, 6)}
            ]
        },
        {
            "name": "Arbitrum",
            "sector": "Infrastructure",
            "category": "L2",
            "description": "Arbitrum is a suite of Ethereum scaling solutions.",
            "rounds": [
                {"type": RoundType.SERIES_B, "amount": 120, "lead": "Lightspeed Venture Partners", "date": datetime(2021, 8, 31)}
            ]
        },
        {
            "name": "Celestia",
            "sector": "Infrastructure",
            "category": "Modular Data Availability",
            "description": "Celestia is a modular data availability network.",
            "rounds": [
                {"type": RoundType.SERIES_B, "amount": 55, "lead": "Bain Capital Crypto", "date": datetime(2022, 10, 19)}
            ]
        },
        {
            "name": "EigenLayer",
            "sector": "Infrastructure",
            "category": "Restaking",
            "description": "EigenLayer is a restaking primitive on Ethereum.",
            "rounds": [
                {"type": RoundType.SERIES_A, "amount": 50, "lead": "Blockchain Capital", "date": datetime(2023, 3, 28)}
            ]
        }
    ]

    for p_data in projects:
        from utils.helpers import slugify
        existing = get_project_by_name(db, p_data["name"])
        if not existing:
            project = Project(
                name=p_data["name"],
                slug=slugify(p_data["name"]),
                sector=p_data["sector"],
                category=p_data["category"],
                description=p_data["description"]
            )
            db.add(project)
            db.flush()
            
            # Add Rounds
            for r in p_data["rounds"]:
                lead_inv = investor_objs.get(r["lead"])
                new_round = FundingRound(
                    project_id=project.id,
                    round_type=r["type"],
                    amount_raised=r["amount"],
                    announced_date=r["date"],
                    lead_investor_id=lead_inv.id if lead_inv else None,
                    source="Genesis"
                )
                db.add(new_round)
                if lead_inv:
                    new_round.investors.append(lead_inv)
            
            # Score the project
            db.flush()
            score, grade = calculate_project_score(project)
            project.grade_score = score
            project.grade_letter = grade
            
            logger.info(f"Loaded Genesis Project: {project.name} (Grade: {grade})")
        else:
            logger.debug(f"Project {p_data['name']} already exists.")

    db.commit()
    db.close()
    logger.success("Genesis data loading complete.")

if __name__ == "__main__":
    load_genesis_data()
