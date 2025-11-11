from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Optional

from bs4 import BeautifulSoup

from .price_parser import ParsedPrice


def parse_price_from_html(
    html: str, *, domain: Optional[str] = None, preferred_currency: str = "EUR"
) -> Optional[ParsedPrice]:
    soup = BeautifulSoup(html, "html.parser")

    price = _price_from_json_ld(soup, preferred_currency=preferred_currency)
    if price:
        return price

    price = _price_from_meta_tags(soup)
    if price:
        return price

    return None


def _price_from_json_ld(
    soup: BeautifulSoup, *, preferred_currency: str
) -> Optional[ParsedPrice]:
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for script in scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
        except json.JSONDecodeError:
            continue

        for candidate in _iter_price_candidates(data):
            value, currency = candidate
            parsed = _build_parsed_price(value, currency or preferred_currency)
            if parsed:
                return parsed
    return None


def _price_from_meta_tags(soup: BeautifulSoup) -> Optional[ParsedPrice]:
    candidate = soup.find(attrs={"itemprop": "price"})
    if candidate:
        if candidate.has_attr("content"):
            parsed = _build_parsed_price(candidate["content"], None)
        else:
            parsed = _build_parsed_price(candidate.get_text(strip=True), None)
        if parsed:
            return parsed

    meta = soup.find("meta", attrs={"property": "product:price:amount"})
    if meta and meta.has_attr("content"):
        parsed = _build_parsed_price(meta["content"], None)
        if parsed:
            return parsed

    return None


def _iter_price_candidates(data: Any) -> Iterable[tuple[Any, Optional[str]]]:
    if isinstance(data, dict):
        if "price" in data:
            currency = (
                data.get("priceCurrency")
                or data.get("currency")
                or data.get("pricecurrency")
            )
            yield (data["price"], currency)

        if "offers" in data:
            yield from _iter_price_candidates(data["offers"])

        for value in data.values():
            yield from _iter_price_candidates(value)

    elif isinstance(data, list):
        for item in data:
            yield from _iter_price_candidates(item)


def _build_parsed_price(value: Any, currency: Optional[str]) -> Optional[ParsedPrice]:
    numeric_value = _coerce_to_float(value)
    if numeric_value is None:
        return None

    display = f"{numeric_value:.2f}".replace(".", ",")
    return ParsedPrice(raw=display, value_eur=numeric_value)


def _coerce_to_float(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        try:
            normalized = value.replace(" ", "").replace(",", ".")
            return float(Decimal(normalized))
        except (InvalidOperation, ValueError):
            return None

    return None
