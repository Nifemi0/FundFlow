"""
Entity Resolution Layer (The Registry).
Ensures data from multiple adapters attaches to the correct canonical entity.
"""

ENTITY_ALIASES = {
    # Format: "alias": "canonical_name"
    "op labs": "Optimism",
    "optimism foundation": "Optimism",
    "union labs": "Union",
    "uniswap labs": "Uniswap",
    "zama.ai": "Zama",
    "irys network": "Irys",
    "arweave bundlr": "Irys",
    "polygon labs": "Polygon",
    "matic": "Polygon"
}

def resolve_entity_name(name: str) -> str:
    """Normalize and resolve aliases to canonical names."""
    n = name.lower().strip()
    return ENTITY_ALIASES.get(n, name)

def get_canonical_id(project) -> str:
    """Helper to get a consistent ID for storage."""
    # Priority: CryptoRank ID > CoinGecko ID > Normalized Name
    ds = project.data_sources or {}
    if ds.get("cryptorank_id"): return f"cr_{ds['cryptorank_id']}"
    if project.coingecko_id: return f"cg_{project.coingecko_id}"
    return project.name.lower().replace(" ", "_")
