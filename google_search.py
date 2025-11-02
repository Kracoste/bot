from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from requests import Response


class GoogleSearchError(RuntimeError):
    """Raised when the Google Search API request fails."""


@dataclass
class GoogleSearchResult:
    title: str
    link: str
    snippet: str


class GoogleSearchClient:
    """Thin wrapper around the Google Custom Search JSON API."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        cse_id: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self._cse_id = cse_id or os.getenv("GOOGLE_CSE_ID")
        self._session = session or requests.Session()

        if not self._api_key:
            raise ValueError(
                "Google API key not provided. Set the GOOGLE_API_KEY environment variable."
            )
        if not self._cse_id:
            raise ValueError(
                "Google Custom Search Engine ID not provided. "
                "Set the GOOGLE_CSE_ID environment variable."
            )

    def search(self, query: str, *, num_results: int = 5) -> List[GoogleSearchResult]:
        """Execute a query and return structured search results."""
        params: Dict[str, Any] = {
            "key": self._api_key,
            "cx": self._cse_id,
            "q": query,
            "num": max(1, min(num_results, 10)),  # API caps per-request results at 10
            "lr": "lang_fr",
            "gl": "fr",
        }
        response = self._session.get(
            "https://www.googleapis.com/customsearch/v1", params=params, timeout=10
        )
        self._raise_for_status(response)
        payload = response.json()
        items = payload.get("items", [])
        results: List[GoogleSearchResult] = []
        for item in items:
            results.append(
                GoogleSearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                )
            )
        return results

    @staticmethod
    def _raise_for_status(response: Response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            message = "Google Search API request failed"
            try:
                details = response.json()
            except ValueError:
                details = response.text
            raise GoogleSearchError(f"{message}: {details}") from exc
