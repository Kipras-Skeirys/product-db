#importlib is Claude's implementation
import importlib

# Adapters raise this on 403/429: the source refuses this bot, the job itself is fine
class SourceBlockedError(Exception):
    pass

def run_job(job, source):
    # Adapters live in the root adapters/ folder: adapters/<adapter name>/data.py
    adapter = importlib.import_module(f"adapters.{source.data_bot_adapter}.data")
    return adapter.ingest(source, job)
