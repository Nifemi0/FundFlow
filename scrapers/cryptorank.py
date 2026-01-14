"""
CryptoRank API scraper for funding data.
Fetches project funding rounds and investor information.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from config.settings import settings, APIEndpoints
from database.models import Project, FundingRound, Investor, RoundType, ProjectStage
from database.queries import (
    get_db,
    get_project_by_name,
    get_investor_by_name,
    log_scraper_run
)


class CryptoRankScraper:
    """Scraper for CryptoRank API."""
    
    def __init__(self):
        self.api_key = settings.cryptorank_api_key
        self.base_url = APIEndpoints.CRYPTORANK_BASE
        self.session = requests.Session()
        # CryptoRank often requires api_key in query params, not headers
        self.default_params = {
            "api_key": self.api_key
        }
        self.session.headers.update({
            "Content-Type": "application/json"
        })
   
    def fetch_recent_funding(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch recent funding rounds from CryptoRank.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of funding round data
        """
        try:
            endpoint = f"{self.base_url}/funding-rounds"
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            params = {
                **self.default_params,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "limit": 100,
                "offset": 0
            }
            
            logger.info(f"Fetching funding rounds from {start_date.date()} to {end_date.date()}")
            
            response = self.session.get(endpoint, params=params)
            
            if response.status_code == 404:
                logger.warning("Main funding endpoint 404. Switching to Currencies fallback.")
                return self._fetch_currencies_fallback(days)
                
            response.raise_for_status()
            
            data = response.json()
            funding_rounds = data.get("data", [])
            
            logger.info(f"Fetched {len(funding_rounds)} funding rounds from CryptoRank")
            
            return funding_rounds
            
        except requests.RequestException as e:
            logger.error(f"CryptoRank API error: {e}")
            return []

    def _fetch_currencies_fallback(self, days: int) -> List[Dict[str, Any]]:
        """Fallback: Fetch recent currencies and format as funding rounds."""
        try:
            endpoint = f"{self.base_url}/currencies"
            params = {
                **self.default_params,
                "limit": 100,
            }
            res = self.session.get(endpoint, params=params)
            res.raise_for_status()
            coins = res.json().get("data", [])
            
            simulated_rounds = []
            now_str = datetime.utcnow().isoformat()
            
            for coin in coins:
                # Mock a funding round structure from coin data
                raised = coin.get("values", {}).get("USD", {}).get("totalRaised")
                
                # Even if they didn't raise publicly, we save them as 'tracked' projects
                # by assigning a nominal amount if they have high market cap
                if not raised:
                    raised = 0
                
                amount_m = float(raised) / 1_000_000
                
                # Ensure we have a date
                announced_date = coin.get("lastUpdated") or now_str
                
                simulated_rounds.append({
                    "project": {
                        "name": coin.get("name"),
                        "sector": coin.get("category"),
                        "description": f"Token: {coin.get('symbol')}. Automatically tracked via CryptoRank fallback.",
                        "website": f"https://cryptorank.io/price/{coin.get('slug')}",
                        "has_token": True,
                        "token_symbol": coin.get("symbol")
                    },
                    "amount_raised": amount_m,
                    "round_type": "Public Sale" if raised > 0 else "Venture Round",
                    "announced_date": announced_date,
                    "investors": []
                })
            
            logger.info(f"Fallback: Generated {len(simulated_rounds)} rounds from coin list.")
            return simulated_rounds
            
        except Exception as e:
            logger.error(f"Fallback failed: {e}")
            return []
    
    def discover_new_projects(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Discovery Mode: Scans project listings on CryptoRank 
        and fetches deep-dive details for each.
        """
        logger.info(f"Discovery Mode: Scanning {limit} listings...")
        try:
            # 1. Get list of projects (Standard ranking/order)
            endpoint = f"{self.base_url}/currencies"
            params = {**self.default_params, "limit": limit}
            res = self.session.get(endpoint, params=params)
            res.raise_for_status()
            coins = res.json().get("data", [])
            
            detailed_projects = []
            for coin in coins[:50]: # Scrutinize the top 50
                coin_id = coin.get("id")
                details = self.fetch_project_details(coin_id)
                if details:
                    # Capture everything available
                    detailed_projects.append({
                        "project": details,
                        "amount_raised": details.get("tokens", {}).get("totalRaised"),
                        "investors": details.get("investors", []),
                        "announced_date": details.get("lastUpdated") or coin.get("created"),
                        "round_type": "Market Tracking"
                    })
            
            return detailed_projects
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            return []

    def fetch_project_details(self, project_id: Any) -> Optional[Dict[str, Any]]:
        """Fetch individual project details (contains rounds)."""
        try:
            endpoint = f"{self.base_url}/currencies/{project_id}"
            response = self.session.get(endpoint, params=self.default_params)
            response.raise_for_status()
            return response.json().get("data")
        except Exception as e:
            logger.error(f"Error fetching detail for project {project_id}: {e}")
            return None
    
    def fetch_investor_details(self, investor_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch investor/VC information.
        
        Args:
            investor_id: CryptoRank investor ID
            
        Returns:
            Investor data dictionary
        """
        try:
            endpoint = f"{self.base_url}/investors/{investor_id}"
            
            response = self.session.get(endpoint, params=self.default_params)
            response.raise_for_status()
            
            data = response.json()
            return data.get("data")
            
        except requests.RequestException as e:
            logger.error(f"Error fetching investor {investor_id}: {e}")
            return None
    
    def process_and_store(self, funding_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Process funding data and store in database.
        
        Args:
            funding_data: List of funding round data from API
            
        Returns:
            Statistics about processing (items_new, items_updated)
        """
        db = get_db()
        stats = {"new": 0, "updated": 0, "errors": 0}
        
        try:
            for item in funding_data:
                try:
                    # Extract project data
                    project_data = item.get("project", {})
                    project_name = project_data.get("name")
                    
                    if not project_name:
                        logger.warning(f"Skipping funding round with no project name: {item}")
                        continue
                    
                    # Get or create project
                    project = get_project_by_name(db, project_name)
                    
                    if not project:
                        project = self._create_project(db, project_data)
                        stats["new"] += 1
                        logger.info(f"Created new project: {project_name}")
                    else:
                        self._update_project(db, project, project_data)
                        stats["updated"] += 1
                    
                    # Process funding round
                    self._process_funding_round(db, project, item)
                    
                    # Process investors
                    investors_data = item.get("investors", [])
                    for inv_data in investors_data:
                        self._process_investor(db, inv_data)
                    
                    # === SCORING INTEGRATION ===
                    # Calculate new score/grade with the updated data
                    from utils.scoring import calculate_project_score
                    score, grade = calculate_project_score(project)
                    project.grade_score = score
                    project.grade_letter = grade
                    project.last_graded = datetime.utcnow()
                    
                    db.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing funding item: {e}")
                    stats["errors"] += 1
                    db.rollback()
                    continue
            
            return stats
            
        finally:
            db.close()
    
    def _create_project(self, db, project_data: Dict[str, Any]) -> Project:
        """Create a new project in database."""
        from utils.helpers import slugify
        
        links = self._extract_links(project_data.get("links", []))
        description = project_data.get("description")
        
        # If no explicit description, maybe check shortDescription if it exists
        if not description:
            description = project_data.get("shortDescription")

        project = Project(
            name=project_data.get("name"),
            slug=slugify(project_data.get("name")),
            description=description,
            website=links.get("website") or project_data.get("website"),
            sector=project_data.get("sector") or project_data.get("category"),
            category=project_data.get("category"),
            stage=self._map_stage(project_data.get("stage")),
            twitter_handle=links.get("twitter"),
            github_url=links.get("github"),
            discord_url=links.get("discord"),
            telegram_url=links.get("telegram"),
            has_token=project_data.get("has_token", False) or project_data.get("type") == "coin",
            token_symbol=project_data.get("symbol"),
            data_sources={"sources": ["CryptoRank"], "cryptorank_id": project_data.get("id")}
        )
        
        db.add(project)
        db.flush()  # Get ID without committing
        
        return project
    
    def _update_project(self, db, project: Project, project_data: Dict[str, Any]):
        """Update existing project with new data."""
        links = self._extract_links(project_data.get("links", []))
        
        # Update only if new data is present
        new_desc = project_data.get("description") or project_data.get("shortDescription")
        if new_desc:
            project.description = new_desc
            
        if links.get("website"):
            project.website = links["website"]
        if links.get("twitter"):
            project.twitter_handle = links["twitter"]
        if links.get("github"):
            project.github_url = links["github"]
        if links.get("discord"):
            project.discord_url = links["discord"]
        if links.get("telegram"):
            project.telegram_url = links["telegram"]
            
        if project_data.get("sector") or project_data.get("category"):
            project.sector = project_data.get("sector") or project_data.get("category")
        
        project.last_updated = datetime.utcnow()
        
        # Add CryptoRank to sources if not already there
        if not project.data_sources:
            project.data_sources = {"sources": ["CryptoRank"], "cryptorank_id": project_data.get("id")}
        elif "CryptoRank" not in project.data_sources.get("sources", []):
            project.data_sources["sources"].append("CryptoRank")
            project.data_sources["cryptorank_id"] = project_data.get("id")
        
        db.flush()

    def _extract_links(self, links_list: List[Dict[str, Any]]) -> Dict[str, str]:
        """Helper to extract common links from CryptoRank links list."""
        extracted = {}
        type_mapping = {
            "web": "website",
            "twitter": "twitter",
            "github": "github",
            "telegram": "telegram",
            "discord": "discord"
        }
        for link in links_list:
            ltype = link.get("type", "").lower()
            if ltype in type_mapping:
                # Store the value, handle potential twitter handle extraction
                val = link.get("value")
                if ltype == "twitter" and val and "twitter.com/" in val:
                    val = val.split("twitter.com/")[-1].strip("/")
                extracted[type_mapping[ltype]] = val
        return extracted
    
    def _process_funding_round(self, db, project: Project, funding_data: Dict[str, Any]):
        """Process and store a funding round."""
        # Check if round already exists (by date and amount)
        announced_date = self._parse_date(funding_data.get("announced_date"))
        if not announced_date:
            announced_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            logger.warning(f"No date for funding round of {project.name}, defaulting to today.")
        
        amount = funding_data.get("amount_raised")
        
        existing = db.query(FundingRound).filter(
            FundingRound.project_id == project.id,
            FundingRound.announced_date == announced_date,
            FundingRound.amount_raised == amount
        ).first()
        
        if existing:
            logger.debug(f"Funding round already exists for {project.name}")
            return
        
        # Create new funding round
        funding_round = FundingRound(
            project_id=project.id,
            round_type=self._map_round_type(funding_data.get("round_type")),
            amount_raised=amount,
            valuation=funding_data.get("valuation"),
            valuation_type=funding_data.get("valuation_type"),
            announced_date=announced_date,
            announcement_url=funding_data.get("source_url"),
            source="CryptoRank"
        )
        
        db.add(funding_round)
        db.flush()
        
        logger.info(f"Added funding round: {project.name} - ${amount}M {funding_data.get('round_type')}")
    
    def _process_investor(self, db, investor_data: Dict[str, Any]) -> Optional[Investor]:
        """Process and store an investor."""
        investor_name = investor_data.get("name")
        
        if not investor_name:
            return None
        
        investor = get_investor_by_name(db, investor_name)
        
        if not investor:
            from utils.helpers import slugify
            from config.settings import TOP_TIER_INVESTORS, TIER_2_INVESTORS
            
            # Determine tier
            tier = 3  # default
            if investor_name.lower() in [inv.lower() for inv in TOP_TIER_INVESTORS]:
                tier = 1
            elif investor_name.lower() in [inv.lower() for inv in TIER_2_INVESTORS]:
                tier = 2
            
            investor = Investor(
                name=investor_name,
                slug=slugify(investor_name),
                type=investor_data.get("type"),
                description=investor_data.get("description"),
                website=investor_data.get("website"),
                tier=tier,
                headquarters=investor_data.get("headquarters"),
                country=investor_data.get("country")
            )
            
            db.add(investor)
            db.flush()
            
            logger.info(f"Added new investor: {investor_name} (Tier {tier})")
        
        return investor
    
    def _map_round_type(self, round_type_str: Optional[str]) -> RoundType:
        """Map string round type to enum."""
        if not round_type_str:
            return RoundType.OTHER
        
        mapping = {
            "seed": RoundType.SEED,
            "private": RoundType.PRIVATE,
            "series a": RoundType.SERIES_A,
            "series b": RoundType.SERIES_B,
            "series c": RoundType.SERIES_C,
            "strategic": RoundType.STRATEGIC,
            "token sale": RoundType.TOKEN_SALE,
            "ido": RoundType.IDO,
            "ico": RoundType.ICO,
            "grant": RoundType.GRANT,
        }
        
        return mapping.get(round_type_str.lower(), RoundType.OTHER)
    
    def _map_stage(self, stage_str: Optional[str]) -> Optional[ProjectStage]:
        """Map string stage to enum."""
        if not stage_str:
            return None
        
        mapping = {
            "concept": ProjectStage.CONCEPT,
            "development": ProjectStage.DEVELOPMENT,
            "testnet": ProjectStage.TESTNET,
            "mainnet": ProjectStage.MAINNET,
            "launched": ProjectStage.LAUNCHED,
        }
        
        return mapping.get(stage_str.lower())
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse date: {date_str}")
            return None

    def sync_project_on_demand(self, project_name: str) -> Optional[Project]:
        """
        Data Mesh Orchestrator (V2).
        Routes discovery and enrichment through authoritative adapters.
        """
        from utils.registry import resolve_entity_name
        canonical_name = resolve_entity_name(project_name)
        
        db = get_db()
        try:
            # Step 1: Resolve Entity
            project = get_project_by_name(db, canonical_name)
            if not project:
                project = get_project_by_name(db, project_name)
                if not project: return None
            
            # Auto-resolve missing GitHub
            if not project.github_url:
                cg_id = project.coingecko_id or project.name
                cg_details = self._fetch_coingecko_details(cg_id)
                if cg_details:
                    project.github_url = cg_details.get("github_url")

            logger.info(f"Data Mesh Sync: {project.name}")
            
            # Step 2: Capital Adapter (Authoritative CryptoRank ID discovery)
            cr_id = project.data_sources.get("cryptorank_id") if project.data_sources else None
            is_newly_verified = False
            
            if not isinstance(cr_id, (int, float)):
                # Search via Symbol or Name
                search_url = f"{self.base_url}/currencies?api_key={self.api_key}&limit=100"
                res = self.session.get(search_url)
                if res.status_code == 200:
                    candidates = res.json().get("data", [])
                    for c in candidates:
                        if (c.get("name") or "").lower() == project.name.lower() or \
                           (c.get("symbol") or "").lower() == (project.token_symbol or "").lower():
                            cr_id = c.get("id")
                            if not project.data_sources: project.data_sources = {}
                            project.data_sources["cryptorank_id"] = cr_id
                            is_newly_verified = True
                            project.verification_source = "CryptoRank Institutional Hub"
                            break
            
            if cr_id:
                details = self.fetch_project_details(cr_id)
                if details:
                    self._update_project(db, project, details)
                    # Process Funding (Authoritative Capital Signal)
                    tokens_field = details.get("tokens", [])
                    total_raised = 0
                    if isinstance(tokens_field, list) and tokens_field:
                        total_raised = tokens_field[0].get("totalRaised") or 0
                    self._process_funding_round(db, project, {
                        **details,
                        "amount_raised": total_raised,
                        "announced_date": details.get("lastUpdated")
                    })
                    project.is_verified = True
                    if not project.verification_source:
                        project.verification_source = "CryptoRank"

            # Step 3: Code Adapter (GitHub Hard Signal)
            from adapters.code import GitHubAdapter
            code_adapter = GitHubAdapter()
            if project.github_url:
                code_stats = code_adapter.fetch_repo_stats(project.github_url)
                if code_stats:
                    project.github_stars = code_stats.get("stars")
                    if not project.data_sources: project.data_sources = {}
                    project.data_sources["commit_velocity"] = code_stats.get("commit_velocity_30d")
                    project.data_sources["code_signal"] = code_adapter.get_code_signal(project.github_url)

            # Step 4: Usage Adapter (DefiLlama)
            from scrapers.defillama import DefiLlamaScraper
            llama = DefiLlamaScraper()
            llama_data = llama.fetch_protocol_stats(project.name, project.token_symbol, project.sector)
            if llama_data:
                project.tvl = llama_data.get("tvl")
                project.revenue_24h = llama_data.get("revenue_24h")
                project.is_verified = True
                project.verification_source = "DefiLlama / Institutional Trackers"

            # Step 5: People Adapter (Hiring/Sign of Life)
            from scrapers.deep_web import DeepScraper
            if project.website:
                web_scraper = DeepScraper()
                if not project.data_sources: project.data_sources = {}
                project.data_sources["hiring_signal"] = web_scraper.get_quality_signal(project.website)

            # Final Rescore (Authoritative weighting)
            from utils.scoring import calculate_project_score
            score, grade = calculate_project_score(project)
            project.grade_score = score
            project.grade_letter = grade
            project.last_graded = datetime.utcnow()
            
            db.commit()
            db.refresh(project)
            return project
        except Exception as e:
            logger.error(f"Mesh sync failed for {project_name}: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    def _fetch_coingecko_details(self, symbol_or_name: str) -> Optional[Dict[str, Any]]:
        """Fetch extra details from CoinGecko public API."""
        try:
            # First search for the id
            search_url = f"https://api.coingecko.com/api/v3/search?query={symbol_or_name}"
            res = self.session.get(search_url)
            if res.status_code == 200:
                coins = res.json().get("coins", [])
                if coins:
                    cg_id = coins[0]["id"]
                    # Get full details
                    detail_url = f"https://api.coingecko.com/api/v3/coins/{cg_id}?localization=false&tickers=false&market_data=false&community_data=false&developer_data=false&sparkline=false"
                    dres = self.session.get(detail_url)
                    if dres.status_code == 200:
                        data = dres.json()
                        links = data.get("links", {})
                        github_repos = links.get("repos_url", {}).get("github", [])
                        return {
                            **data,
                            "github_url": github_repos[0] if github_repos else None
                        }
            return None
        except Exception:
            return None



    def discover_project(self, query: str, query_type: Any = None) -> Optional[Project]:
        """Proactively find a project from external sources if not in local DB."""
        import re
        # Clean query: remove @ and handle (Name) patterns
        base_query = query.replace("@", "").strip()
        
        # Look for (AltName) and extract it
        alt_match = re.search(r"\((.*?)\)", base_query)
        alt_query = alt_match.group(1).strip() if alt_match else None
        
        # Remove parentheses from primary query
        base_query = re.sub(r"\(.*?\)", "", base_query).strip()
        
        # Generate variations: strata_fi -> ["strata_fi", "strata fi", "strata"]
        terms_to_try = [base_query]
        if "_" in base_query:
            terms_to_try.append(base_query.replace("_", " "))
            terms_to_try.append(base_query.split("_")[0])
        if alt_query:
            terms_to_try.append(alt_query)
        
        # Deduplicate and filter
        terms_to_try = list(dict.fromkeys([t for t in terms_to_try if t and len(t) > 2]))
        
        db = get_db()
        try:
            from database.queries import search_projects, get_project_by_name
            # Check for exact matches or high-quality fuzzy match already in DB
            for term in terms_to_try:
                project = get_project_by_name(db, term)
                if project:
                    logger.info(f"Project '{term}' found in local database. Syncing...")
                    return self.sync_project_on_demand(project.name)
            
            logger.info(f"External discovery for terms: {terms_to_try}")
            
            # 1. Search CoinGecko first
            for term in terms_to_try:
                search_url = f"https://api.coingecko.com/api/v3/search?query={term}"
                res = self.session.get(search_url, timeout=10)
                if res.status_code == 200:
                    coins = res.json().get("coins", [])
                    if coins:
                        # Try to find the best match (often the first if not too common)
                        top = coins[0]
                        from utils.helpers import slugify
                        
                        # Check if already exists
                        existing = db.query(Project).filter(Project.name == top["name"]).first()
                        if existing:
                            logger.info(f"Project {top['name']} already exists, skipping creation.")
                            return self.sync_project_on_demand(existing.name)

                        # Deep discovery via details
                        cg_details = self._fetch_coingecko_details(top["id"]) or {}
                        
                        project = Project(
                            name=top["name"],
                            slug=slugify(top["name"]),
                            token_symbol=top["symbol"],
                            coingecko_id=top["id"],
                            github_url=cg_details.get("github_url"),
                            sector=cg_details.get("asset_platform_id"), # Use chain as sector if found
                            description=cg_details.get("description", {}).get("en") if isinstance(cg_details.get("description"), dict) else None,
                            is_verified=True,
                            verification_source="CoinGecko Tracker"
                        )
                        db.add(project)
                        db.commit()
                        db.refresh(project)
                        return self.sync_project_on_demand(project.name)
                
                # Sleep briefly between terms to avoid rate limit
                time.sleep(1)
            
            # 2. Universal Web Fallback (Deep Search) - MANDATORY if trackers fail
            logger.info(f"Trackers failed for {query}. Launching Deep Research Fallback...")
            from scrapers.news import NewsScraper
            from adapters.research import WebResearchAdapter
            
            ns = NewsScraper(api_key=settings.newsapi_key)
            researcher = WebResearchAdapter(newsapi_key=settings.newsapi_key)
            
            # Strategy: Detect Domain/Handle specifics early
            from utils.classifier import QueryType
            if query_type == QueryType.DOMAIN:
                # Use clean_query if possible, or term
                existing = db.query(Project).filter(Project.website.ilike(f"%{query}%")).first()
                if existing: return self.sync_project_on_demand(existing.name)
            
            if query_type == QueryType.HANDLE:
                existing = db.query(Project).filter(Project.twitter_handle.ilike(f"%{query}%")).first()
                if existing: return self.sync_project_on_demand(existing.name)

            for term in terms_to_try:
                identity = researcher.research_project_identity(term, query_type=query_type)
                if identity:
                    from utils.helpers import slugify
                    
                    project_name = identity.get("name") or term
                    project_slug = slugify(project_name)
                    
                    # FINAL SAFETY CHECK: Does this slug already exist?
                    existing = db.query(Project).filter(Project.slug == project_slug).first()
                    if existing:
                        logger.info(f"Project with slug '{project_slug}' already exists. Syncing...")
                        return self.sync_project_on_demand(existing.name)

                    project = Project(
                        name=project_name,
                        slug=project_slug,
                        website=identity.get("website"),
                        twitter_handle=identity.get("twitter"),
                        github_url=identity.get("github_url"),
                        telegram_url=identity.get("telegram"),
                        discord_url=identity.get("discord"),
                        sector=identity.get("sector_hint"),
                        description=identity.get("description") or f"Automatically discovered project: {project_name}",
                        data_confidence=40, # Increased confidence due to deep forensics
                        is_verified=False,
                        verification_source=f"Deep Forensic Mesh via {query_type.value if query_type else 'Manual Query'}",
                        stage=ProjectStage.DEVELOPMENT,
                        data_sources={
                            "sources": ["Identity Scraper", "Web Forensic Mesh"],
                            "hiring_signal": identity.get("hiring"),
                            "linkedin_url": identity.get("linkedin")
                        }
                    )
                    db.add(project)
                    db.commit()
                    db.refresh(project)
                    logger.success(f"Forensic Discovery: '{project_name}' ingested. Hiring: {identity.get('hiring')}")
                    return self.sync_project_on_demand(project.name)
            
            return None
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    async def discover_project_async(self, query: str, query_type: Any = None) -> Optional[Project]:
        """Async wrapper for discover_project."""
        import asyncio
        return await asyncio.to_thread(self.discover_project, query, query_type)

def run_cryptorank_scraper(days: int = 30) -> Dict[str, Any]:
    """
    Main function to run CryptoRank scraper.
    
    Args:
        days: Number of days to look back
        
    Returns:
        Scraper statistics
    """
    logger.info("Starting CryptoRank scraper...")
    
    scraper = CryptoRankScraper()
    
    try:
        # 1. Attempt standard funding fetch
        funding_data = scraper.fetch_recent_funding(days=days)
        
        # 2. ALSO run Discovery Mode to catch EVERYTHING new on the platform
        new_projects_data = scraper.discover_new_projects(limit=50)
        
        # Combine data
        combined_data = funding_data + new_projects_data
        
        if not combined_data:
            logger.warning("No data found from any source.")
            return {"status": "no_data", "items": 0}
        
        # Process and store
        stats = scraper.process_and_store(combined_data)
        
        # Log run
        db = get_db()
        try:
            log_scraper_run(
                db,
                scraper_name="cryptorank",
                status="success",
                items_collected=len(funding_data),
                items_new=stats["new"],
                items_updated=stats["updated"]
            )
        finally:
            db.close()
        
        logger.info(f"CryptoRank scraper completed: {stats['new']} new, {stats['updated']} updated")
        
        return {
            "status": "success",
            "items_collected": len(funding_data),
            **stats
        }
        
    except Exception as e:
        logger.error(f"CryptoRank scraper failed: {e}")
        
        db = get_db()
        try:
            log_scraper_run(
                db,
                scraper_name="cryptorank",
                status="failed",
                errors=[str(e)]
            )
        finally:
            db.close()
        
        return {"status": "failed", "error": str(e)}


if __name__ == "__main__":
    # For testing
    result = run_cryptorank_scraper(days=7)
    print(result)
