from psycopg.rows import class_row
from psycopg.types.json import Jsonb
from models.discovery_queue import DiscoveryQueue
from config import MAX_ATTEMPTS

def create_discovery_queue_row(conn, job):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO discovery_queue (data_sources_id, context) VALUES (%s, %s)
        """, (job.data_sources_id, Jsonb(job.context)))

def claim_discovery_queue_row(conn, claimed_by, cooling_source_ids):
    with conn.cursor(row_factory=class_row(DiscoveryQueue)) as cur:
        cur.execute("""
            UPDATE discovery_queue
            SET status = 'in_progress', claimed_at = now(), claimed_by = %s
            WHERE id = (
                SELECT discovery_queue.id FROM discovery_queue
                JOIN data_sources ON data_sources.id = discovery_queue.data_sources_id
                WHERE discovery_queue.status = 'pending'
                AND discovery_queue.attempt_count < %s
                AND data_sources.status = 'active'
                AND discovery_queue.data_sources_id <> ALL(%s::uuid[])
                ORDER BY discovery_queue.id
                LIMIT 1
                FOR UPDATE OF discovery_queue SKIP LOCKED
            )
            RETURNING id, data_sources_id, context, claimed_at
        """, (claimed_by, MAX_ATTEMPTS, cooling_source_ids))
        return cur.fetchone()

def delete_discovery_queue_row(conn, id, claimed_by):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM discovery_queue
            WHERE id = %s AND claimed_by = %s
        """, (id, claimed_by))
        return cur.rowcount == 1

def release_discovery_queue_row(conn, id, claimed_by, count_attempt=True):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE discovery_queue
            SET status = 'pending', claimed_at = NULL, claimed_by = NULL, attempt_count = attempt_count + %s
            WHERE id = %s AND claimed_by = %s
        """, (1 if count_attempt else 0, id, claimed_by))
