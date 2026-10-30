from psycopg.rows import class_row
from models.product_job import ProductJob
from config import MAX_ATTEMPTS, INGESTION_INTERVAL_DAYS

def claim_product_queue_row(conn, claimed_by, cooling_source_ids):
    with conn.cursor(row_factory=class_row(ProductJob)) as cur:
        cur.execute("""
            UPDATE product_queue
            SET status = 'in_progress', claimed_at = now(), claimed_by = %s
            WHERE id = (
                SELECT product_queue.id FROM product_queue
                JOIN data_sources ON data_sources.id = product_queue.data_sources_id
                WHERE product_queue.status = 'waiting'
                AND product_queue.next_ingestion_due <= now()
                AND product_queue.attempt_count < %s
                AND data_sources.status = 'active'
                AND product_queue.data_sources_id <> ALL(%s::uuid[])
                ORDER BY product_queue.next_ingestion_due
                LIMIT 1
                FOR UPDATE OF product_queue SKIP LOCKED
            )
            RETURNING id, data_sources_id, product_url, context
        """, (claimed_by, MAX_ATTEMPTS, cooling_source_ids))
        return cur.fetchone()

def finish_product_queue_row(conn, id, raw_ingestions_id):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE product_queue
            SET status = 'waiting', claimed_at = NULL, claimed_by = NULL, attempt_count = 0, attempt_logs = '[]',
                last_raw_ingestions_id = %s, next_ingestion_due = now() + make_interval(days => %s)
            WHERE id = %s
        """, (raw_ingestions_id, INGESTION_INTERVAL_DAYS, id))

def release_product_queue_row(conn, id, error, count_attempt=True):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE product_queue
            SET status = 'waiting', claimed_at = NULL, claimed_by = NULL, attempt_count = attempt_count + %s,
                attempt_logs = attempt_logs || jsonb_build_array(jsonb_build_object('at', now(), 'error', %s::text))
            WHERE id = %s
        """, (1 if count_attempt else 0, error, id))
