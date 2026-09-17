from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extensions import connection
import os

pool = ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=os.getenv("DB_URL")
)

@contextmanager
def get_connection() -> connection:
    conn = pool.getconn()

    try: 
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        pool.putconn(conn)