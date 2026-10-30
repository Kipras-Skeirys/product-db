from psycopg.rows import class_row
from models.data_source import DataSource

def get_source(conn, data_sources_id):
    with conn.cursor(row_factory=class_row(DataSource)) as cur:
        cur.execute("""
            SELECT id, name, rate_limit_ms, data_bot_adapter
            FROM data_sources
            WHERE id = %s
        """, (data_sources_id,))
        return cur.fetchone()
