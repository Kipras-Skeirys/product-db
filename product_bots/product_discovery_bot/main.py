import db
import scheduler
from repositories import data_sources_repository as data_sources
from config import DB_DSN
import json
import os

# Claude Code made function
def register_sources(db_manager):
    # Every adapters/<adapter name>/source.json becomes a row in data_sources
    with db_manager.get_connection() as conn:
        for adapter_name in os.listdir("adapters"):
            config_path = f"adapters/{adapter_name}/source.json"
            if not os.path.exists(config_path):
                continue
            with open(config_path) as f:
                config = json.load(f)
            data_sources.upsert_source(conn, adapter_name, config)
            print(f"Registered source {config['name']}")

try:
    with db.ConnectionPoolManager(DB_DSN) as db_manager:
        register_sources(db_manager)
        scheduler.run(db_manager)

except KeyboardInterrupt:
    print("Shutdown signal received, exiting cleanly.")
