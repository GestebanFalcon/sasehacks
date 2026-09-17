from .connect import get_connection
from pandas import DataFrame

# --- Nontrivial Operations ---
# (contain complete and useful logic with their own conn)

def init_chat(df: DataFrame, response: str) -> str:
    """Takes in fetched reviews, creates a new session, adds new reviews, and creates a new message

    Returns new session ID"""
    print("connecting")
    with get_connection() as conn:
        print("connected")
        with conn.cursor() as cur:
            print("inserting")
            cur.execute("""
                INSERT INTO sessions DEFAULT VALUES RETURNING id
            """)
            id = cur.fetchone()[0]
            print(id)
            
            for row in df.itertuples():
                cur.execute("""
                    INSERT INTO reviews (content, embedding, review_time, rating, account_id, session_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (row.review_text, row.embedding.tolist(), row.time, row.rating, row.account_id, id)
                )

            cur.execute("""
                INSERT INTO messages (content, role, session_id)
                VALUES (%s, %s, %s)
            """, (response, "assistant", id))


            return id

# --- Trivial Operations ---
# (take conn as input)

#could perhaps group up message inputs idk
def insert_message(conn, content, role, session_id):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO messages (content, role, session_id)
            VALUES (%s, %s, %s)
        """, (content, role, session_id))

def delete_session(conn, session_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM sessions
            WHERE id = %s
        """, (session_id,))
        rows_deleted = cur.rowcount #can check if bad things happened idk.
        return rows_deleted
