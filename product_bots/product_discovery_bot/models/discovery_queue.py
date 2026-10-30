from dataclasses import dataclass
from uuid import UUID
from typing import Any
from datetime import datetime

@dataclass
class DiscoveryQueue:
    id: int
    data_sources_id: UUID
    context: dict[str, Any]
    claimed_at: datetime