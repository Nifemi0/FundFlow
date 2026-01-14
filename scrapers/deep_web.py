"""
DeepScraper for FundFlow.
Scrapes project websites to find raw signals: Team mentions, Hiring status, and Blog activity.
"""
import requests
from bs4 import BeautifulSoup
from loguru import logger
from typing import Dict, Any, Optional
import re

class DeepScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape_project_site(self, url: str) -> Dict[str, Any]:
        """Scrape the project homepage for qualitative signals."""
        if not url: return {}
        
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code != 200:
                return {"error": f"Status {res.status_code}"}
            
            soup = BeautifulSoup(res.text, 'lxml')
            text = soup.get_text().lower()
            
            signals = {
                "hiring": any(word in text for word in ["hiring", "careers", "join us", "open positions"]),
                "docs_found": any(word in text for word in ["documentation", "docs", "whitepaper", "developers"]),
                "team_section": any(word in text for word in ["team", "about us", "founders"]),
                "blog_active": any(word in text for word in ["blog", "medium", "mirror", "updates"])
            }
            
            # Try to find a Meta Description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                signals["scraped_description"] = meta_desc.get("content")
                
            return signals
        except Exception as e:
            logger.error(f"DeepScraper error for {url}: {e}")
            return {"error": str(e)}

    def get_quality_signal(self, url: str) -> str:
        """Returns a string description of the site quality."""
        data = self.scrape_project_site(url)
        if "error" in data: return "Site Unreachable"
        
        score = 0
        if data.get("hiring"): score += 1
        if data.get("docs_found"): score += 1
        if data.get("blog_active"): score += 1
        
        if score >= 3: return "Active Development (High)"
        if score >= 1: return "Live & Building (Medium)"
        return "Minimal Presence (Low)"
