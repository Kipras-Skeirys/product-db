from dataclasses import dataclass
from typing import Any

@dataclass
class ProductJob:
    product_url: str
    context: dict[str, Any]
