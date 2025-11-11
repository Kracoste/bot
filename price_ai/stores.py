from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Store:
    name: str
    domain: str

    def build_query(self, product: str) -> str:
        # Focus the search on the store domain and price-related keywords.
        return f"{product} prix site:{self.domain}"


STORES: List[Store] = [
    Store(name="Point.P", domain="pointp.fr"),
    Store(name="Brico Dépôt", domain="bricodepot.fr"),
    Store(name="Castorama", domain="castorama.fr"),
]
