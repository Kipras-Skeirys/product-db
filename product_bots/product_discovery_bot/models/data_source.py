from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

@dataclass
class DataSource:
    id: UUID
    name: str
    rate_limit_ms: int
    discovery_interval: timedelta
    discovery_bot_adapter: str