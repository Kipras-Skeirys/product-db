from psycopg.types.json import Jsonb

def insert_raw_ingestion(conn, data_sources_id, payload, ingested_by):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO raw_ingestions (data_sources_id, payload, ingested_by) VALUES (%s, %s, %s)
            RETURNING id
        """, (data_sources_id, Jsonb(payload), ingested_by))
        return cur.fetchone()[0]
