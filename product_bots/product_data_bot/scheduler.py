from repositories import data_sources_repository as data_sources
from repositories import product_queue_repository as product_queue
from config import BOT_NAME, IDLE_SECONDS, MAX_BACKOFF_MS, BLOCKED_BACKOFF_MS, MAX_BLOCKED_BACKOFF_MS
import coordinator

import time

next_allowed = {}  # source id -> time when this bot can send the next request to that source
delay_ms = {}      # source id -> current delay between requests, grows on failures

def claim_next_job(db_manager):
    now = time.time()
    cooling_source_ids = []
    for source_id, allowed_at in next_allowed.items():
        if allowed_at > now:
            cooling_source_ids.append(source_id)

    with db_manager.get_connection() as conn:
        job = product_queue.claim_product_queue_row(conn, BOT_NAME, cooling_source_ids)
        if job is None:
            return None, None
        source = data_sources.get_source(conn, job.data_sources_id)

    return job, source

def run(db_manager):
    while True:
        job, source = claim_next_job(db_manager)

        if job is None:
            time.sleep(IDLE_SECONDS)
            continue

        if source.id not in delay_ms:
            delay_ms[source.id] = source.rate_limit_ms
        next_allowed[source.id] = time.time() + delay_ms[source.id] / 1000

        result = coordinator.run_job(db_manager, job, source)
        if result == "done":
            delay_ms[source.id] = source.rate_limit_ms
        elif result == "failed":
            delay_ms[source.id] = min(delay_ms[source.id] * 2, MAX_BACKOFF_MS)
        elif result == "blocked":
            # Wait at least BLOCKED_BACKOFF_MS before this bot sends that source anything again
            delay_ms[source.id] = min(max(delay_ms[source.id] * 2, BLOCKED_BACKOFF_MS), MAX_BLOCKED_BACKOFF_MS)
            next_allowed[source.id] = time.time() + delay_ms[source.id] / 1000
