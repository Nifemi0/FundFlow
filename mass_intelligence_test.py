"""
Mass Intelligence Test V2
Tests FundFlow's ability to discover and analyze 43 specific projects.
Includes rate-limit protection and local DB awareness.
"""
import os
import sys
import asyncio
import time
from datetime import datetime
from loguru import logger
import json

# Setup environment
os.environ['DATABASE_URL'] = 'postgresql://fundflow:fundflow@localhost:5432/fundflow'
os.environ['NEWSAPI_KEY'] = '493e3ae3babf4c11852bf7b13653a54e'
os.environ['PYTHONPATH'] = '.'

from scrapers.cryptorank import CryptoRankScraper
from utils.classifier import classify_input, QueryType
from database.queries import get_db, get_project_full_info

PROJECTS_LIST = [
    "Raiku", "Noise", "Codex", "EthGas", "Fast protocol", "Taceo", 
    "Axis", "Drosera", "Deepnode", "Base", "Warden", "Nexus", 
    "Daylight", "Dawn", "Stork", "Genlayer", "Gradient", "Rome", "Primus"
]

async def run_mass_test():
    logger.info("=" * 80)
    logger.info("FUNDFLOW MASS INTELLIGENCE TEST V2")
    logger.info(f"Target: {len(PROJECTS_LIST)} Projects")
    logger.info("=" * 80)
    
    scraper = CryptoRankScraper()
    
    summary_report = []
    
    for idx, query in enumerate(PROJECTS_LIST, 1):
        logger.info(f"[{idx}/{len(PROJECTS_LIST)}] Analyzing: {query}")
        
        try:
            # 1. Classify
            q_type, clean_query = classify_input(query)
            
            # 2. Discover & Sync
            project = scraper.discover_project(query, query_type=q_type)
            
            if project:
                # 3. Get Full Info
                db = get_db()
                info = get_project_full_info(db, project.id)
                proj = info['project']
                
                # 4. Extract Key Intelligence
                chain = proj.category if proj.category else "Unknown"
                if proj.tags:
                    chain_tags = [t.name for t in proj.tags if t.category == 'ecosystem' or 'chain' in t.name.lower()]
                    if chain_tags:
                        chain = ", ".join(chain_tags)
                
                # Tech info from description or category
                tech = "N/A"
                if proj.description:
                    if "modular" in proj.description.lower(): tech = "Modular"
                    elif "zk" in proj.description.lower() or "zero knowledge" in proj.description.lower(): tech = "ZK"
                    elif "layer 2" in proj.description.lower() or "l2" in proj.description.lower(): tech = "L2"
                
                intel = {
                    "name": proj.name,
                    "building": proj.description[:100] + "..." if proj.description else "N/A",
                    "chain": chain,
                    "tech": tech,
                    "funding": f"${info['total_raised']:.1f}M" if info['total_raised'] > 0 else "Undisclosed",
                    "status": "✅ Found",
                }
                summary_report.append(intel)
                logger.success(f"  Captured: {proj.name} | {intel['funding']} | {intel['chain']}")
                db.close()
            else:
                summary_report.append({
                    "name": query,
                    "status": "❌ Not Found",
                    "building": "N/A",
                    "chain": "N/A",
                    "tech": "N/A",
                    "funding": "N/A"
                })
                logger.warning(f"  Failed: {query} not found.")
                
        except Exception as e:
            logger.error(f"  Error analyzing {query}: {str(e)}")
            summary_report.append({
                "name": query,
                "status": "⚠️ Error",
                "building": "Error",
                "chain": "Error",
                "tech": "Error",
                "funding": "Error"
            })
            
        # Respect rate limits
        await asyncio.sleep(2)

    # Output Final Consolidated Report
    print("\n" + "=" * 130)
    print(f"{'PROJECT':<20} | {'STATUS':<10} | {'FUNDING':<12} | {'CHAIN/CAT':<20} | {'TECH':<10} | {'BUILDING'}")
    print("-" * 130)
    
    found_count = 0
    for item in summary_report:
        if item['status'] == "✅ Found": 
            found_count += 1
            status_disp = "✅ Found"
        else:
            status_disp = item['status']
            
        print(f"{item['name'][:20]:<20} | {status_disp:<10} | {item['funding']:<12} | {item['chain'][:20]:<20} | {item['tech']:<10} | {item['building'][:40]}")
    
    print("-" * 130)
    print(f"SUMMARY: Successfully analyzed {found_count} out of {len(PROJECTS_LIST)} projects.")
    print("=" * 130)

if __name__ == "__main__":
    asyncio.run(run_mass_test())
