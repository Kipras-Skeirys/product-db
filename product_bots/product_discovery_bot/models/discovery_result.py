from dataclasses import dataclass
from typing import Any
from models.product_job import ProductJob

@dataclass
class DiscoveryResult:
    product_jobs: list[ProductJob]
    next_contexts: list[dict[str, Any]]
