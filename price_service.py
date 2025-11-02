from __future__ import annotations

import html
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests

from google_search import GoogleSearchClient, GoogleSearchError, GoogleSearchResult
from price_parser import ParsedPrice, extract_price
from store_parsers import parse_price_from_html
from stores import STORES, Store


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}


@dataclass
class StorePrice:
    store: Store
    result: Optional[GoogleSearchResult]
    price: Optional[ParsedPrice]
    source: str = "unknown"


class PriceLookupService:
    """Encapsulates Google search + site parsing to retrieve store prices."""

    def __init__(
        self,
        *,
        client: Optional[GoogleSearchClient] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._client = client or GoogleSearchClient()
        self._session = session or requests.Session()

    def lookup(
        self, product: str, *, per_store_results: int = 3
    ) -> List[StorePrice]:
        per_store_results = max(1, min(per_store_results, 10))
        results: List[StorePrice] = []
        for store in STORES:
            results.append(
                self._find_price_for_store(
                    store,
                    product,
                    per_store_results=per_store_results,
                )
            )
        return results

    def _find_price_for_store(
        self,
        store: Store,
        product: str,
        *,
        per_store_results: int,
    ) -> StorePrice:
        query = store.build_query(product)
        try:
            results = self._client.search(query, num_results=per_store_results)
        except GoogleSearchError as error:
            raise RuntimeError(
                f"Erreur lors de la requête Google pour {store.name}: {error}"
            ) from error

        best_result: Optional[GoogleSearchResult] = None
        parsed_price: Optional[ParsedPrice] = None
        price_source = "unknown"

        for result in results:
            price = extract_price(result.snippet)
            source = "snippet" if price else "unknown"
            if not price:
                price = self._fetch_price_from_page(result.link, store=store)
                if price:
                    source = "page"
            if price:
                best_result = result
                parsed_price = price
                price_source = source
                break

        if best_result is None and results:
            best_result = results[0]

        return StorePrice(
            store=store, result=best_result, price=parsed_price, source=price_source
        )

    def _fetch_price_from_page(
        self, url: str, *, store: Store, timeout: int = 12
    ) -> Optional[ParsedPrice]:
        try:
            response = self._session.get(url, headers=REQUEST_HEADERS, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException:
            return None

        text = html.unescape(response.text)
        parsed = parse_price_from_html(text, domain=store.domain)
        if parsed:
            return parsed

        return None


def format_store_prices(store_prices: Iterable[StorePrice]) -> str:
    lines: List[str] = []
    for store_price in store_prices:
        if store_price.result is None:
            lines.append(f"- {store_price.store.name}: aucun résultat trouvé.")
            continue

        if store_price.price:
            price_part = f"{store_price.price.raw} €"
            if store_price.source == "page":
                price_part += " (page magasin)"
            elif store_price.source == "snippet":
                price_part += " (extrait Google)"
        else:
            price_part = "prix non détecté"

        lines.append(
            f"- {store_price.store.name}: {price_part}\n"
            f"  {store_price.result.title}\n"
            f"  {store_price.result.link}"
        )
    return "\n".join(lines)
