from __future__ import annotations

import re
from typing import List, Optional

from .models import PlanMeasurement

LxW_PATTERN = re.compile(
    r"(?P<label>[A-Za-zÀ-ÿ0-9\s\-\(\)]{2,})?"
    r"[:\-]?\s*(?P<val1>\d+(?:[.,]\d+)?)\s*(?P<unit1>cm|m)"
    r"\s*[x×]\s*(?P<val2>\d+(?:[.,]\d+)?)\s*(?P<unit2>cm|m)",
    flags=re.IGNORECASE,
)

AREA_PATTERN = re.compile(
    r"(?P<label>[A-Za-zÀ-ÿ0-9\s\-\(\)]{2,})?"
    r"[:\-]?\s*(?P<area>\d+(?:[.,]\d+)?)\s*(?:m²|m2)\b",
    flags=re.IGNORECASE,
)

AREA_TRAILING_PATTERN = re.compile(
    r"(?P<area>\d+(?:[.,]\d+)?)\s*(?:m²|m2)\s*(?P<label>[A-Za-zÀ-ÿ0-9\s\-\(\)]{2,})",
    flags=re.IGNORECASE,
)

LENGTH_PATTERN = re.compile(
    r"(?P<label>[A-Za-zÀ-ÿ0-9\s\-\(\)]{2,})?"
    r"[:\-]?\s*(?P<length>\d+(?:[.,]\d+)?)\s*(?P<unit>m|cm)\b",
    flags=re.IGNORECASE,
)

LENGTH_TRAILING_PATTERN = re.compile(
    r"(?P<length>\d+(?:[.,]\d+)?)\s*(?P<unit>m|cm)\s*(?P<label>[A-Za-zÀ-ÿ0-9\s\-\(\)]{2,})",
    flags=re.IGNORECASE,
)

def parse_measurements_from_text(text: str) -> List[PlanMeasurement]:
    measurements: List[PlanMeasurement] = []
    seen_tokens: set[str] = set()

    def add_measurement(label: str, area: Optional[float], length: Optional[float], width: Optional[float]) -> None:
        token = f"{label}|{area}|{length}|{width}"
        if token in seen_tokens:
            return
        seen_tokens.add(token)
        measurements.append(
            PlanMeasurement(
                label=label.title() if label else "Zone",
                area_m2=area,
                length_m=length,
                width_m=width,
                source="text",
            )
        )

    for match in LxW_PATTERN.finditer(text):
        label = _sanitize_label(match.group("label"))
        val1 = _to_meters(match.group("val1"), match.group("unit1"))
        val2 = _to_meters(match.group("val2"), match.group("unit2"))
        area = val1 * val2
        add_measurement(label, area, val1, val2)

    for match in AREA_PATTERN.finditer(text):
        label = _sanitize_label(match.group("label"))
        area = _to_float(match.group("area"))
        add_measurement(label, area, None, None)

    for match in AREA_TRAILING_PATTERN.finditer(text):
        label = _sanitize_label(match.group("label"))
        area = _to_float(match.group("area"))
        add_measurement(label, area, None, None)

    for match in LENGTH_PATTERN.finditer(text):
        label = _sanitize_label(match.group("label"))
        length = _to_meters(match.group("length"), match.group("unit"))
        add_measurement(label, None, length, None)

    for match in LENGTH_TRAILING_PATTERN.finditer(text):
        label = _sanitize_label(match.group("label"))
        length = _to_meters(match.group("length"), match.group("unit"))
        add_measurement(label, None, length, None)

    return measurements


def _sanitize_label(raw: Optional[str]) -> str:
    if not raw:
        return ""
    label = " ".join(raw.split())
    label = label.replace("cm", "").replace("m", "").strip(" :-")
    return label.strip()


def _to_float(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def _to_meters(value: Optional[str], unit: Optional[str]) -> float:
    number = _to_float(value) or 0.0
    if not unit:
        return number
    unit = unit.lower()
    if unit == "cm":
        return number / 100
    return number
