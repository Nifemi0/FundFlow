from sqlalchemy import text
from database.queries import engine
from loguru import logger

def migrate_v2():
    columns = [
        ("tvl", "FLOAT"),
        ("tvl_30d_change", "FLOAT"),
        ("dau", "INTEGER"),
        ("daily_tx", "INTEGER"),
        ("revenue_24h", "FLOAT"),
        ("data_confidence", "FLOAT DEFAULT 0"),
        ("scoring_breakdown", "JSON"),
        ("risk_factors", "JSON")
    ]
    
    with engine.connect() as conn:
        for name, type_ in columns:
            try:
                conn.execute(text(f"ALTER TABLE projects ADD COLUMN {name} {type_}"))
                logger.info(f"Added column {name}")
            except Exception as e:
                logger.debug(f"Column {name} might already exist: {e}")
        conn.commit()
    logger.success("Migration to V2 complete.")

if __name__ == "__main__":
    migrate_v2()
