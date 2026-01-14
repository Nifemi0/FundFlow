import requests
import re
from loguru import logger
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

class WebResearchAdapter:
    """
    The 'Final Fallback' for the Data Mesh.
    If a project isn't on any tracker, this adapter hunts for its 
    official website and social presence via news and search signals.
    """
    def __init__(self, newsapi_key: str):
        self.newsapi_key = newsapi_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (http://fundflow.ai/bot)"
        })

    def research_project_identity(self, query: str, query_type: Any = None) -> Dict[str, Any]:
        """Forensic research: Scrape, Parse Structured Data, and Scan sub-links."""
        from utils.classifier import QueryType
        logger.info(f"Universal Research: Conducting deep forensics on {query} ({query_type})...")
        
        results = {
            "name": None, 
            "website": None, 
            "github_url": None, 
            "twitter": None, 
            "discord": None,
            "telegram": None,
            "linkedin": None,
            "description": None,
            "hiring": False,
            "sector_hint": None
        }
        clean_query = query.lower().replace(" ", "").replace("@", "")

        # 0. Initial Resolution
        if query_type == QueryType.DOMAIN:
            results["website"] = f"https://{query}" if not query.startswith("http") else query
        elif query_type == QueryType.SLUG:
            results["github_url"] = f"https://github.com/{query}"
        elif query_type == QueryType.HANDLE:
            results["twitter"] = query.replace("@", "")
            self._hunt_website_from_handle(results)

        # 1. Search for Footprint (if website still missing)
        if not results["website"]:
            self._hunt_website_via_search(query, clean_query, results)

        # 2. Deep Forensic Scrape
        if results["website"]:
            try:
                self._scrape_and_parse(results["website"], results, depth=1)
            except Exception as e:
                logger.warning(f"Forensic scrape failed for {results['website']}: {e}")

        # Final Cleanup & Identity Synthesis
        if not results["twitter"] and query_type == QueryType.HANDLE:
            results["twitter"] = clean_query

        if not results["name"]:
            results["name"] = query.replace("@", "").capitalize()

        return results

    def _scrape_and_parse(self, url: str, results: Dict[str, Any], depth: int = 1):
        """Scrape a page, parse JSON-LD, and optionally follow sub-links."""
        try:
            res = self.session.get(url, timeout=10)
            if res.status_code != 200: return
            
            soup = BeautifulSoup(res.text, 'lxml')
            
            # A. Parse JSON-LD (Structured Data)
            self._parse_json_ld(soup, results)
            
            # B. Identity from Title
            title_tag = soup.find("title")
            if title_tag and not results["name"]:
                results["name"] = title_tag.text.split("|")[0].split("-")[0].split(":")[0].strip()

            # C. Extract Signals from Links
            found_sublinks = []
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                full_href = href if href.startswith("http") else f"{url.rstrip('/')}/{href.lstrip('/')}"
                
                # Socials
                if "github.com/" in href and not results["github_url"]:
                    results["github_url"] = link['href']
                if ("twitter.com/" in href or "x.com/" in href) and not results["twitter"]:
                    results["twitter"] = href.split(".com/")[-1].strip("/")
                if "t.me/" in href and not results["telegram"]:
                    results["telegram"] = href.split("t.me/")[-1].strip("/")
                if "discord.gg/" in href or "discord.com/invite/" in href:
                    results["discord"] = href
                if "linkedin.com/company/" in href:
                    results["linkedin"] = href

                # Sublink Discovery (Docs, Team, Careers)
                if any(k in href for k in ["docs.", "documentation", "/docs", "/whitepaper", "/team", "/about", "/careers", "/jobs"]):
                    if depth > 0 and full_href.startswith(url):
                        found_sublinks.append(full_href)
                
                # Hiring Signal
                if any(k in href for k in ["careers", "jobs", "hiring"]):
                    results["hiring"] = True

            # D. Sector Guessing
            page_text = soup.get_text().lower()
            keywords = {
                "infrastructure": ["blockchain", "layer 1", "layer 2", "consensus", "scaling"],
                "defi": ["liquidity", "yield", "protocol", "exchange", "dex", "trading"],
                "security": ["audit", "threat", "protection", "monitoring", "shield"],
                "ai": ["intelligence", "model", "training", "compute", "agent"]
            }
            if not results["sector_hint"]:
                for sector, keys in keywords.items():
                    if any(k in page_text for k in keys):
                        results["sector_hint"] = sector.capitalize()
                        break

            # E. Metadata
            if not results["description"]:
                meta = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
                if meta: results["description"] = meta["content"]

            # F. Recursive Scan
            if depth > 0:
                for sub in list(set(found_sublinks))[:2]: # Scan up to 2 high-value sublinks
                    self._scrape_and_parse(sub, results, depth=0)

        except Exception: pass

    def _parse_json_ld(self, soup: BeautifulSoup, results: Dict[str, Any]):
        """Parse Schema.org / JSON-LD for identity data."""
        import json
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get("@type") in ["Organization", "Corporation", "SoftwareApplication"]:
                        if not results["name"]: results["name"] = data.get("name")
                        if not results["description"]: results["description"] = data.get("description")
            except Exception: continue

    def _hunt_website_via_search(self, query: str, clean_query: str, results: Dict[str, Any]):
        """Hunt for a website using news/search APIs."""
        queries = [f'"{query}" crypto official', f'"{query}" funding protocol']
        for q in queries:
            url = "https://newsapi.org/v2/everything"
            params = {"q": q, "apiKey": self.newsapi_key, "pageSize": 5}
            try:
                res = self.session.get(url, params=params)
                if res.status_code == 200:
                    for art in res.json().get("articles", []):
                        text = (art.get("url") or "") + " " + (art.get("description") or "") + " " + (art.get("title") or "")
                        found_urls = re.findall(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)', text)
                        for f_url in found_urls:
                            f_url = f_url.rstrip(".,)/")
                            if any(x in f_url.lower() for x in ["twitter.com", "t.me", "medium.com", "news.", "globenewswire", "cryptorank", "coingecko"]):
                                continue
                            if clean_query in f_url.lower() and not results["website"]:
                                results["website"] = f_url
                                return
            except Exception: pass

    def _hunt_website_from_handle(self, results: Dict[str, Any]):
        """Try to find a website given a twitter handle."""
        handle = results.get("twitter")
        if not handle: return
        url = "https://newsapi.org/v2/everything"
        params = {"q": f"twitter.com/{handle}", "apiKey": self.newsapi_key, "pageSize": 3}
        try:
            res = self.session.get(url, params=params)
            if res.status_code == 200:
                for art in res.json().get("articles", []):
                    text = (art.get("description") or "") + " " + (art.get("content") or "")
                    found_urls = re.findall(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)', text)
                    for f_url in found_urls:
                        if "twitter.com" not in f_url and "t.me" not in f_url:
                            results["website"] = f_url.rstrip(".,)/")
                            return
        except Exception: pass
