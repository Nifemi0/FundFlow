"""
GitHub vertical adapter for FundFlow.
Determines "Hard Signal" developer velocity.
"""
import requests
from loguru import logger
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class GitHubAdapter:
    def __init__(self, token: Optional[str] = None):
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})

    def fetch_repo_stats(self, repo_url: str) -> Dict[str, Any]:
        """Deep dive into repository velocity."""
        if not repo_url or "github.com/" not in repo_url:
            return {}
        
        try:
            # Extract owner/repo
            path = repo_url.split("github.com/")[-1].strip("/")
            parts = path.split("/")
            if len(parts) < 1: return {}
            
            owner = parts[0]
            repo = parts[1] if len(parts) > 1 else None
            
            if not repo:
                # Resolve most popular repo for an organization
                org_repos_url = f"https://api.github.com/orgs/{owner}/repos"
                res = self.session.get(org_repos_url, params={"sort": "pushed", "per_page": 5}, timeout=10)
                if res.status_code == 200:
                    repos = res.json()
                    if repos:
                        # Pick repo with most stars
                        best_repo = max(repos, key=lambda x: x.get("stargazers_count", 0))
                        repo = best_repo.get("name")
                    else: return {}
                else: return {}

            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            res = self.session.get(api_url, timeout=10)
            if res.status_code != 200: return {}
            
            data = res.json()
            
            # Fetch Activity (Commits in last 30 days)
            # Use the search API or stats endpoint
            commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
            since = (datetime.utcnow() - timedelta(days=30)).isoformat()
            cres = self.session.get(commits_url, params={"since": since}, timeout=10)
            commit_count = len(cres.json()) if cres.status_code == 200 else 0
            
            return {
                "stars": data.get("stargazers_count"),
                "forks": data.get("forks_count"),
                "open_issues": data.get("open_issues_count"),
                "last_commit": data.get("pushed_at"),
                "commit_velocity_30d": commit_count,
                "is_active": commit_count > 5
            }
        except Exception as e:
            logger.error(f"GitHub Adapter error for {repo_url}: {e}")
            return {}

    def get_code_signal(self, repo_url: str) -> str:
        """Returns a qualitative developer health signal."""
        stats = self.fetch_repo_stats(repo_url)
        if not stats: return "No Public Code Found"
        
        velocity = stats.get("commit_velocity_30d", 0)
        if velocity > 50: return "Industrial Grade Shipping (High)"
        if velocity > 10: return "Actively Maintained (Medium)"
        if velocity > 0: return "Slow/Maintenance Mode (Low)"
        return "Stale Repository"
