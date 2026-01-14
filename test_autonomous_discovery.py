"""
Autonomous Discovery Stress Test
Tests FundFlow's ability to discover 100 random crypto projects without manual intervention.
Mix of: Twitter handles, project names, domains, and GitHub slugs.
"""
import os
import sys
from datetime import datetime
from loguru import logger

# Setup environment
os.environ['DATABASE_URL'] = 'postgresql://fundflow:fundflow@localhost:5432/fundflow'
os.environ['NEWSAPI_KEY'] = '493e3ae3babf4c11852bf7b13653a54e'
os.environ['PYTHONPATH'] = '.'

from scrapers.cryptorank import CryptoRankScraper
from utils.classifier import classify_input
from database.queries import get_db

# 100 Real Crypto Projects (Mixed Format)
TEST_PROJECTS = [
    # Tier 1 - Major Projects (Should find easily)
    "uniswap", "optimism", "@arbitrum", "polygon", "avalanche",
    "solana", "ethereum", "cosmos", "polkadot", "chainlink",
    
    # Tier 2 - Mid-tier (Mix of handles and names)
    "@starknet", "zksync", "@base", "celestia", "@eigenlayer",
    "lido", "@aave", "compound", "@makerdao", "curve",
    
    # Tier 3 - Newer Projects (Handles)
    "@monad_xyz", "@berachain", "@megaeth", "@movement_labs", "@fuel_network",
    "@scroll_zkp", "@linea", "@manta_network", "@taiko_xyz", "@zircuit",
    
    # Tier 4 - Infrastructure (Domains)
    "drosera.io", "hyperlane.xyz", "layerzero.network", "wormhole.com", "axelar.network",
    "espresso.systems", "babylon.io", "symbiotic.fi", "karak.network", "ethos.xyz",
    
    # Tier 5 - DeFi Protocols
    "@pendle_fi", "@gearbox_protocol", "@morpho_labs", "@euler_finance", "@radiant_capital",
    "@notional_finance", "@ribbon_finance", "@tempus_finance", "@sense_finance", "@yield",
    
    # Tier 6 - Gaming/NFT
    "@immutable", "@axieinfinity", "@decentraland", "@sandbox", "@illuvium",
    "@gala_games", "@myria_games", "@treasure_dao", "@pixels_online", "@shrapnel_game",
    
    # Tier 7 - Privacy/ZK
    "@aztecnetwork", "@railgun_project", "@nocturne_xyz", "@penumbra_zone", "@aleo",
    "zcash", "monero", "@ironfish", "@namada", "@anoma",
    
    # Tier 8 - Data/Oracle
    "@chainlink", "@api3dao", "@pyth_network", "@redstone_defi", "@supra_oracle",
    "@chronicle_labs", "@tellor", "@dia_data", "@bandprotocol", "@umbrella_network",
    
    # Tier 9 - Infra/Tooling
    "@thegraph", "@goldsky_io", "@subsquid", "@envio_indexer", "@fhenix_io",
    "@inco_network", "@zama_fhe", "@sunscreen_tech", "@renegade_fi", "@flash_trade",
    
    # Tier 10 - Emerging/Stealth (Very Hard)
    "@userocket_app", "@strata_fi", "redotpay", "@bitrobot", "@ethgas",
    "@zen_chain", "@union_build", "irys", "@bundlr", "@arweave"
]

def run_discovery_test():
    """Run the autonomous discovery stress test."""
    logger.info("=" * 80)
    logger.info("FUNDFLOW AUTONOMOUS DISCOVERY STRESS TEST")
    logger.info(f"Testing {len(TEST_PROJECTS)} projects")
    logger.info("=" * 80)
    
    scraper = CryptoRankScraper()
    db = get_db()
    
    results = {
        "total": len(TEST_PROJECTS),
        "found": 0,
        "not_found": 0,
        "errors": 0,
        "by_tier": {},
        "details": []
    }
    
    for idx, query in enumerate(TEST_PROJECTS, 1):
        tier = f"Tier {(idx - 1) // 10 + 1}"
        if tier not in results["by_tier"]:
            results["by_tier"][tier] = {"found": 0, "total": 0}
        
        results["by_tier"][tier]["total"] += 1
        
        logger.info(f"\n[{idx}/{len(TEST_PROJECTS)}] Testing: {query}")
        
        try:
            # Classify input
            query_type, clean_query = classify_input(query)
            logger.info(f"  Classified as: {query_type.value}")
            
            # Attempt discovery
            project = scraper.discover_project(query, query_type=query_type)
            
            if project:
                logger.success(f"  ✅ FOUND: {project.name}")
                results["found"] += 1
                results["by_tier"][tier]["found"] += 1
                results["details"].append({
                    "query": query,
                    "status": "FOUND",
                    "project_name": project.name,
                    "tier": tier,
                    "query_type": query_type.value
                })
            else:
                logger.warning(f"  ❌ NOT FOUND")
                results["not_found"] += 1
                results["details"].append({
                    "query": query,
                    "status": "NOT_FOUND",
                    "tier": tier,
                    "query_type": query_type.value
                })
                
        except Exception as e:
            logger.error(f"  ⚠️ ERROR: {str(e)[:100]}")
            results["errors"] += 1
            results["details"].append({
                "query": query,
                "status": "ERROR",
                "error": str(e)[:200],
                "tier": tier
            })
    
    # Generate Report
    logger.info("\n" + "=" * 80)
    logger.info("FINAL RESULTS")
    logger.info("=" * 80)
    logger.info(f"Total Projects Tested: {results['total']}")
    logger.info(f"✅ Successfully Found: {results['found']} ({results['found']/results['total']*100:.1f}%)")
    logger.info(f"❌ Not Found: {results['not_found']} ({results['not_found']/results['total']*100:.1f}%)")
    logger.info(f"⚠️ Errors: {results['errors']} ({results['errors']/results['total']*100:.1f}%)")
    
    logger.info("\n" + "-" * 80)
    logger.info("BREAKDOWN BY TIER")
    logger.info("-" * 80)
    for tier, stats in sorted(results["by_tier"].items()):
        success_rate = stats["found"] / stats["total"] * 100 if stats["total"] > 0 else 0
        logger.info(f"{tier}: {stats['found']}/{stats['total']} ({success_rate:.1f}%)")
    
    # Save detailed results
    import json
    with open("discovery_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("\n" + "=" * 80)
    logger.info("Detailed results saved to: discovery_test_results.json")
    logger.info("=" * 80)
    
    db.close()
    return results

if __name__ == "__main__":
    run_discovery_test()
