from dataclasses import dataclass
from uuid import UUID
from typing import Any

@dataclass
class ProductJob:
    id: int
    data_sources_id: UUID
    product_url: str
    context: dict[str, Any]
