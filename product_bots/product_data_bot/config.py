from dotenv import load_dotenv
import os
import socket

load_dotenv()

# Name saved in claimed_by, so a stuck job shows which server and process held it
BOT_NAME = f"{socket.gethostname()}:{os.getpid()}"

# Database credentials
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

DB_DSN = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

# scheduler.py config
IDLE_SECONDS = 1
MAX_ATTEMPTS = 3
MAX_BACKOFF_MS = 60000
BLOCKED_BACKOFF_MS = 300000
MAX_BLOCKED_BACKOFF_MS = 3600000

# coordinator.py config
INGESTION_INTERVAL_DAYS = 7

# adapters config
REQUEST_TIMEOUT = 30
