from __future__ import annotations

import json
from typing import List

from price_ai.price_service import PriceLookupService, StorePrice


class BackendPriceService:
    def __init__(self) -> None:
        self.service = PriceLookupService()

    def lookup(self, query: str, *, per_store_results: int = 3) -> List[StorePrice]:
        return self.service.lookup(query, per_store_results=per_store_results)

    @staticmethod
    def serialize(store_prices: List[StorePrice]) -> str:
        return json.dumps(
            [
                {
                    "store": sp.store.name,
                    "title": sp.result.title if sp.result else "",
                    "link": sp.result.link if sp.result else "",
                    "price": sp.price.raw if sp.price else None,
                    "source": sp.source,
                }
                for sp in store_prices
            ],
            ensure_ascii=False,
        )
