from psycopg.types.json import Jsonb

def insert_product_jobs(conn, data_sources_id, product_jobs):
    rows = []
    for job in product_jobs:
        rows.append((data_sources_id, job.product_url, Jsonb(job.context)))

    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO product_queue (data_sources_id, product_url, context) VALUES (%s, %s, %s)
            ON CONFLICT (product_url) DO UPDATE SET context = EXCLUDED.context
        """, rows)
