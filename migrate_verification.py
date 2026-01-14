"""
Migration script to add is_verified and verification_source to projects table.
"""
import os
from sqlalchemy import create_engine, text

# Setup environment
os.environ['DATABASE_URL'] = 'postgresql://fundflow:fundflow@localhost:5432/fundflow'
database_url = os.environ['DATABASE_URL']

def migrate():
    engine = create_engine(database_url)
    with engine.connect() as conn:
        print("Starting migration...")
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"))
            print("Added is_verified column.")
        except Exception as e:
            print(f"Column is_verified might already exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN verification_source VARCHAR(100)"))
            print("Added verification_source column.")
        except Exception as e:
            print(f"Column verification_source might already exist: {e}")
            
        conn.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate()
