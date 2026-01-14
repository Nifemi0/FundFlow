"""
DefiLlama Adapter for FundFlow.
Fetches protocol-native metrics: TVL, Volume, and Revenue.
"""
import requests
from loguru import logger
from typing import Dict, Any, Optional

class DefiLlamaScraper:
    BASE_URL = "https://api.llama.fi"
    
    def __init__(self):
        self._protocols_cache = None

    def _get_protocols(self):
        if not self._protocols_cache:
            try:
                res = requests.get(f"{self.BASE_URL}/protocols", timeout=10)
                if res.status_code == 200:
                    self._protocols_cache = res.json()
            except Exception as e:
                logger.error(f"Failed to fetch protocols list: {e}")
        return self._protocols_cache or []

    def fetch_protocol_stats(self, name: str, symbol: Optional[str] = None, sector: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find best matching protocol or chain and return stats."""
        # 0. If it's a known L1/L2, prioritize chain stats
        if sector in ["L1", "L2", "Infrastructure", "Layer 2", "Layer 1"]:
            chain_data = self.fetch_chain_stats(name)
            if chain_data:
                return chain_data

        protocols = self._get_protocols()
        
        # 1. Try exact name match
        best_match = None
        name_lower = name.lower()
        symbol_lower = symbol.lower() if symbol else None
        
        for p in protocols:
            p_name = p.get('name', '').lower()
            p_symbol = p.get('symbol', '').lower()
            
            # Avoid bridges for protocol search if name is just the chain
            if "-bridge" in p.get('slug', '') and name_lower not in p.get('slug', ''):
                continue

            if p_name == name_lower:
                best_match = p
                break
            if symbol_lower and p_symbol == symbol_lower:
                if not best_match or (p.get('tvl', 0) or 0) > (best_match.get('tvl', 0) or 0):
                    best_match = p
        
        # Fuzzy match
        if not best_match:
            for p in protocols:
                if name_lower in p.get('name', '').lower():
                    if not best_match or (p.get('tvl', 0) or 0) > (best_match.get('tvl', 0) or 0):
                        best_match = p
                        
        if best_match:
            slug = best_match.get("slug")
            fees_data = self.fetch_fees(slug)
            
            if isinstance(fees_data, list) and len(fees_data) > 0:
                fees_data = fees_data[0]
            elif not isinstance(fees_data, dict):
                fees_data = {}
            
            return {
                "tvl": best_match.get("tvl"),
                "category": best_match.get("category"),
                "chains": best_match.get("chains"),
                "change_7d": best_match.get("change_7d"),
                "revenue_24h": fees_data.get("total24h"),
                "slug": slug
            }
        
        # Final fallback
        return self.fetch_chain_stats(name)

    def fetch_fees(self, slug: str) -> Optional[Dict[str, Any]]:
        """Fetch daily fees/revenue for a protocol slug."""
        try:
            url = f"https://api.llama.fi/summary/fees/{slug}"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception:
            return None

    def fetch_chain_stats(self, chain_name: str) -> Optional[Dict[str, Any]]:
        """Fetch chain-level TVL (e.g., Optimism)."""
        # Canonicalize common chain names
        chain_map = {
            "optimism": "Optimism",
            "arbitrum": "Arbitrum",
            "polygon": "Polygon",
            "avalanche": "Avalanche",
            "base": "Base"
        }
        name = chain_map.get(chain_name.lower(), chain_name.capitalize())
        
        try:
            url = f"https://api.llama.fi/v2/historicalChainTvl/{name}"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data and isinstance(data, list):
                    latest = data[-1]
                    # Calculate 30d delta
                    prev_30d = data[-30] if len(data) >= 30 else data[0]
                    tvl_change = 0
                    if prev_30d.get('tvl', 0) > 0:
                        tvl_change = ((latest['tvl'] - prev_30d['tvl']) / prev_30d['tvl']) * 100
                    
                    return {
                        "tvl": latest.get("tvl"),
                        "tvl_30d_change": tvl_change,
                        "category": "L1/L2 Infrastructure"
                    }
            return None
        except Exception as e:
            return None
