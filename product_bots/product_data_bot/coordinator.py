from repositories import product_queue_repository as product_queue
from repositories import raw_ingestions_repository as raw_ingestions
from worker import SourceBlockedError
from config import BOT_NAME
import worker

def save_success(db_manager, job, source, payload):
    with db_manager.get_connection() as conn:
        raw_ingestions_id = raw_ingestions.insert_raw_ingestion(conn, source.id, payload, BOT_NAME)
        product_queue.finish_product_queue_row(conn, job.id, raw_ingestions_id)

    print(f"Job {job.id} done: {job.product_url}")

def save_failure(db_manager, job, source, error):
    with db_manager.get_connection() as conn:
        product_queue.release_product_queue_row(conn, job.id, error)

    print(f"Job {job.id} failed: {error}")

def save_blocked(db_manager, job, source, error):
    # Only this bot is blocked, so the job goes back for other bots without counting as a failed attempt
    with db_manager.get_connection() as conn:
        product_queue.release_product_queue_row(conn, job.id, error, count_attempt=False)

    print(f"Job {job.id} blocked by {source.name}: {error}, backing off")

def run_job(db_manager, job, source):
    try:
        payload = worker.run_job(job, source)
        save_success(db_manager, job, source, payload)
        return "done"

    except SourceBlockedError as e:
        save_blocked(db_manager, job, source, str(e))
        return "blocked"

    except Exception as e:
        save_failure(db_manager, job, source, str(e))
        return "failed"
