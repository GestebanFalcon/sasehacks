from pathlib import Path
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
with psycopg2.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS migrations(
            version INT PRIMARY KEY
        )
        """)

        for migration in sorted(Path("db/migrations").glob("*.sql")):
            version = int(migration.stem.split("_")[0])

            cur.execute(
                "SELECT 1 FROM migrations WHERE version = %s",
                (version,)
            )
            exists = cur.fetchone()

            if exists:
                continue

            sql = migration.read_text()
            
            cur.execute(sql)

            cur.execute("INSERT INTO MIGRATIONS (version) VALUES (%s)", (version,))

            

        
