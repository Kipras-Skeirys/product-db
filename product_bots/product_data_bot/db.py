import psycopg_pool
from contextlib import contextmanager
    
class ConnectionPoolManager:

    def __init__(self, DSN):
        try:
            self.pool = psycopg_pool.ConnectionPool(DSN)
            self.pool.wait()
        except psycopg_pool.PoolTimeout as e:
            raise RuntimeError("Pool timed out before establishing a connection") from e
        except RuntimeError as e:
            raise RuntimeError("There was an error connecting to the database") from e

    @contextmanager
    def get_connection(self):
        with self.pool.connection() as conn:
            yield conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.close()