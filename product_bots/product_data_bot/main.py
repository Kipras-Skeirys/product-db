import db
import scheduler
from config import DB_DSN

try:
    with db.ConnectionPoolManager(DB_DSN) as db_manager:
        scheduler.run(db_manager)

except KeyboardInterrupt:
    print("Shutdown signal received, exiting cleanly.")
