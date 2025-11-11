from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


PRICE_PATTERN = re.compile(
    r"(\d{1,3}(?:[ \u00A0.]\d{3})*(?:[.,]\d{2})?)\s?[€\u20AC]"
)


@dataclass
class ParsedPrice:
    raw: str
    value_eur: float


def extract_price(text: str) -> Optional[ParsedPrice]:
    """Extract the first price occurrence from a text snippet."""
    if not text:
        return None

    match = PRICE_PATTERN.search(text)
    if not match:
        return None

    raw_price = match.group(1)
    normalized = (
        raw_price.replace(" ", "")
        .replace("\u00A0", "")
        .replace(".", "")
        .replace(",", ".")
    )
    try:
        value = float(normalized)
    except ValueError:
        return None

    return ParsedPrice(raw=raw_price, value_eur=value)
