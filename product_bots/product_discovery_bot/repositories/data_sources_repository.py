from psycopg.rows import class_row
from models.data_source import DataSource

def claim_due_source(conn):
    with conn.cursor(row_factory=class_row(DataSource)) as cur:
        cur.execute("""
            UPDATE data_sources
            SET next_discovery_due = now() + discovery_interval, discovery_status = 'in_progress'
            WHERE id = (
                SELECT id FROM data_sources
                WHERE status = 'active'
                AND next_discovery_due <= now()
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id, name, rate_limit_ms, discovery_interval, discovery_bot_adapter
        """)
        return cur.fetchone()

def upsert_source(conn, adapter_name, config):
    # status is only set on the first insert, so a source turned off by hand stays off after a restart
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO data_sources (name, base_url, rate_limit_ms, status, discovery_bot_adapter, data_bot_adapter)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET base_url = EXCLUDED.base_url, rate_limit_ms = EXCLUDED.rate_limit_ms
        """, (config["name"], config["base_url"], config["rate_limit_ms"], config["status"], adapter_name, adapter_name))

def get_source(conn, data_sources_id):
    with conn.cursor(row_factory=class_row(DataSource)) as cur:
        cur.execute("""
            SELECT id, name, rate_limit_ms, discovery_interval, discovery_bot_adapter
            FROM data_sources
            WHERE id = %s
        """, (data_sources_id,))
        return cur.fetchone()

def add_source_failure(conn, data_sources_id):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE data_sources SET consecutive_failures = consecutive_failures + 1
            WHERE id = %s
        """, (data_sources_id,))

def reset_source_failures(conn, data_sources_id):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE data_sources SET consecutive_failures = 0
            WHERE id = %s
        """, (data_sources_id,))

def finish_discovery_if_done(conn, data_sources_id):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE data_sources SET discovery_status = 'waiting'
            WHERE id = %s
            AND NOT EXISTS (SELECT 1 FROM discovery_queue WHERE data_sources_id = data_sources.id)
        """, (data_sources_id,))
        return cur.rowcount == 1
