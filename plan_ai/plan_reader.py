from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

try:
    import pdfplumber
except ImportError:  # pragma: no cover - optional dependency
    pdfplumber = None

try:
    import cv2  # type: ignore
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency
    cv2 = None  # type: ignore
    np = None  # type: ignore

try:
    import pytesseract
except ImportError:  # pragma: no cover - optional dependency
    pytesseract = None

from shared.utils import log_info, require_dependency


MEASUREMENT_PATTERN = re.compile(
    r"(?P<label>[A-Za-zÀ-ÿ0-9\s-]{3,})[:\-]?\s*"
    r"(?:(?P<area>\d+(?:[.,]\d+)?)\s*(?:m²|m2))?"
    r"(?:.*?(?P<length>\d+(?:[.,]\d+)?)\s*m)?",
    flags=re.IGNORECASE,
)


@dataclass
class PlanMeasurement:
    label: str
    area_m2: Optional[float] = None
    length_m: Optional[float] = None
    width_m: Optional[float] = None


@dataclass
class PlanAnalysis:
    source: Path
    measurements: List[PlanMeasurement]
    raw_text: str


class PlanReader:
    """Best-effort OCR/PDF extraction to capture measurements from plans."""

    def __init__(self, *, dpi: int = 300) -> None:
        self._dpi = dpi

    def read(self, path: str | Path) -> PlanAnalysis:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        log_info(f"Lecture du plan: {file_path}")
        raw_text = self._extract_text(file_path)
        measurements = self._parse_measurements(raw_text)
        return PlanAnalysis(source=file_path, measurements=measurements, raw_text=raw_text)

    def _extract_text(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            require_dependency(pdfplumber, "pdfplumber")
            return self._extract_pdf_text(file_path)
        else:
            require_dependency(cv2, "opencv-python")
            require_dependency(pytesseract, "pytesseract")
            return self._extract_image_text(file_path)

    def _extract_pdf_text(self, file_path: Path) -> str:
        text_chunks: List[str] = []
        assert pdfplumber is not None
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text_chunks.append(page.extract_text() or "")
        return "\n".join(text_chunks)

    def _extract_image_text(self, file_path: Path) -> str:
        assert cv2 is not None and pytesseract is not None
        image = cv2.imread(str(file_path))
        if image is None:
            raise RuntimeError(f"Impossible de lire l'image: {file_path}")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), sigmaX=0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text = pytesseract.image_to_string(thresh, lang="fra")
        return text

    def _parse_measurements(self, text: str) -> List[PlanMeasurement]:
        measurements: List[PlanMeasurement] = []
        for match in MEASUREMENT_PATTERN.finditer(text):
            label = " ".join(match.group("label").split())
            if not label:
                continue

            area = self._safe_float(match.group("area"))
            length = self._safe_float(match.group("length"))
            measurement = PlanMeasurement(label=label, area_m2=area, length_m=length)
            measurements.append(measurement)

        return measurements

    @staticmethod
    def _safe_float(value: Optional[str]) -> Optional[float]:
        if not value:
            return None
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None
