from dataclasses import dataclass
from uuid import UUID

@dataclass
class DataSource:
    id: UUID
    name: str
    rate_limit_ms: int
    data_bot_adapter: str
