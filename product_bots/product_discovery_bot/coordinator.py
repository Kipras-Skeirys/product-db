from repositories import data_sources_repository as data_sources
from repositories import discovery_queue_repository as discovery_queue
from repositories import product_queue_repository as product_queue
from models.discovery_job import DiscoveryJob
from config import BOT_NAME
from worker import SourceBlockedError
import worker

def save_success(db_manager, job, source, result):
    finished = False
    with db_manager.get_connection() as conn:
        # Only save if this bot still owns the job (the reaper could have taken it back)
        if discovery_queue.delete_discovery_queue_row(conn, job.id, BOT_NAME):
            product_queue.insert_product_jobs(conn, source.id, result.product_jobs)
            for context in result.next_contexts:
                discovery_queue.create_discovery_queue_row(conn, DiscoveryJob(source.id, context))
            data_sources.reset_source_failures(conn, source.id)
            finished = data_sources.finish_discovery_if_done(conn, source.id)

    print(f"Job {job.id} done: {len(result.product_jobs)} products, {len(result.next_contexts)} next jobs")
    if finished:
        print(f"Discovery for {source.name} finished")

def save_failure(db_manager, job, source, error):
    with db_manager.get_connection() as conn:
        discovery_queue.release_discovery_queue_row(conn, job.id, BOT_NAME)
        data_sources.add_source_failure(conn, source.id)

    print(f"Job {job.id} failed: {error}")

def save_blocked(db_manager, job, source, error):
    # Only this bot is blocked, so the job goes back for other bots without counting as a failed attempt
    with db_manager.get_connection() as conn:
        discovery_queue.release_discovery_queue_row(conn, job.id, BOT_NAME, count_attempt=False)

    print(f"Job {job.id} blocked by {source.name}: {error}, backing off")

def run_job(db_manager, job, source):
    try:
        result = worker.run_job(job, source)
        save_success(db_manager, job, source, result)
        return "done"

    except SourceBlockedError as e:
        save_blocked(db_manager, job, source, str(e))
        return "blocked"

    except Exception as e:
        save_failure(db_manager, job, source, str(e))
        return "failed"
