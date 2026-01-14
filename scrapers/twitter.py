"""
Twitter API scraper for social metrics.
Fetches user profiles and engagement stats using Twitter API v2.
"""
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from config.settings import settings, APIEndpoints
from database.queries import get_db, get_project_by_slug
from database.models import Project

class TwitterScraper:
    """Scraper for Twitter API v2."""
    
    def __init__(self):
        self.bearer_token = settings.twitter_bearer_token
        self.base_url = APIEndpoints.TWITTER_BASE
        
        if not self.bearer_token:
            logger.warning("Twitter Bearer Token not set. Social data will differ.")
            
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "FundFlowBot/1.0"
        }

    def fetch_user_metrics(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch public metrics for a Twitter username.
        
        Args:
            username: Twitter handle (without @)
            
        Returns:
            Dict containing followers_count, following_count, tweet_count, etc.
        """
        if not self.bearer_token:
            return None
            
        try:
            # Clean username just in case
            username = username.strip().replace("@", "")
            
            endpoint = f"{self.base_url}/2/users/by/username/{username}"
            params = {
                "user.fields": "public_metrics,created_at,verified"
            }
            
            response = requests.get(
                endpoint,
                headers=self._get_headers(),
                params=params,
                timeout=10
            )
            
            if response.status_code == 429:
                logger.warning(f"Twitter API Rate Limit hit for {username}")
                return None
                
            response.raise_for_status()
            
            data = response.json()
            if "data" not in data:
                logger.warning(f"Twitter user '{username}' not found.")
                return None
                
            user_data = data["data"]
            metrics = user_data.get("public_metrics", {})
            
            return {
                "followers_count": metrics.get("followers_count", 0),
                "following_count": metrics.get("following_count", 0),
                "tweet_count": metrics.get("tweet_count", 0),
                "listed_count": metrics.get("listed_count", 0),
                "id": user_data.get("id"),
                "verified": user_data.get("verified", False)
            }
            
        except requests.RequestException as e:
            logger.error(f"Twitter API error for {username}: {e}")
            return None

    def update_project_socials(self, project: Project) -> bool:
        """
        Update a single project's social metrics in the DB.
        """
        if not project.twitter_handle:
            return False
            
        metrics = self.fetch_user_metrics(project.twitter_handle)
        
        if metrics:
            project.twitter_followers = metrics["followers_count"]
            # We could store other metrics in a JSON field if we expand the model,
            # but for now follower count is the key metric for scoring.
            return True
        return False

def run_twitter_enrichment(limit: int = 50):
    """
    Batch job to update social stats for recent projects.
    """
    logger.info("Starting Twitter enrichment job...")
    
    db = get_db()
    scraper = TwitterScraper()
    
    try:
        # Find projects with twitter handles but no follower count, 
        # OR projects not updated in 7 days.
        # For MVP, just grab the most recently updated ones to refresh them.
        projects = db.query(Project).filter(
            Project.twitter_handle.isnot(None)
        ).order_by(
            Project.last_updated.desc()
        ).limit(limit).all()
        
        updated_count = 0
        
        for project in projects:
            if scraper.update_project_socials(project):
                updated_count += 1
                
        db.commit()
        logger.info(f"Updated Twitter stats for {updated_count} projects.")
        
    finally:
        db.close()

if __name__ == "__main__":
    run_twitter_enrichment()
