"""
NewsAPI Adapter for FundFlow.
Fetches recent news and sentiment for startups and projects.
"""
import requests
from loguru import logger
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class NewsScraper:
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_project_news(self, project_name: str) -> List[Dict[str, Any]]:
        """Search for recent news mentions of a project."""
        try:
            # Search within the last 30 days
            from_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
            url = f"{self.BASE_URL}/everything"
            params = {
                "q": f'"{project_name}" AND (crypto OR blockchain OR funding)',
                "from": from_date,
                "sortBy": "relevancy",
                "language": "en",
                "apiKey": self.api_key,
                "pageSize": 5
            }
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                articles = res.json().get("articles", [])
                return articles
            return []
        except Exception as e:
            logger.error(f"NewsAPI error for {project_name}: {e}")
            return []

    def get_news_sentiment_signal(self, project_name: str) -> str:
        """Simple signal: How many news hits in the last 30 days?"""
        articles = self.fetch_project_news(project_name)
        count = len(articles)
        if count >= 5: return "High Press Coverage"
        if count >= 2: return "Emerging Awareness"
        if count > 0: return "Single Mention"
        return "Silent"
