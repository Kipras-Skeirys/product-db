from dataclasses import dataclass
from uuid import UUID
from typing import Any

@dataclass
class DiscoveryJob:
    data_sources_id: UUID
    context:  dict[str, Any]