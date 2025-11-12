from __future__ import annotations

import re
from pathlib import Path
from typing import List

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
    from pytesseract import TesseractNotFoundError
except ImportError:  # pragma: no cover - optional dependency
    pytesseract = None
    TesseractNotFoundError = None

from shared.utils import log_info, require_dependency
from .dimension_parser import parse_measurements_from_text
from .models import PlanAnalysis, PlanMeasurement


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
        measurements = parse_measurements_from_text(raw_text)
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
        try:
            pytesseract.get_tesseract_version()
        except (TesseractNotFoundError, OSError) as exc:  # type: ignore[arg-type]
            raise RuntimeError(
                "Tesseract OCR n'est pas installé ou introuvable dans le PATH. "
                "Installez-le (macOS: brew install tesseract, Linux: sudo apt install tesseract-ocr)."
            ) from exc
        image = cv2.imread(str(file_path))
        if image is None:
            raise RuntimeError(f"Impossible de lire l'image: {file_path}")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), sigmaX=0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        target_lang = self._pick_language()
        text = pytesseract.image_to_string(thresh, lang=target_lang)
        return text

    @staticmethod
    def _pick_language() -> str:
        """Use French OCR if available, otherwise fallback to English."""
        try:
            languages = pytesseract.get_languages(config="")  # type: ignore[attr-defined]
        except Exception:
            languages = ["eng"]
        if "fra" in languages:
            return "fra"
        if "eng" in languages:
            return "eng"
        raise RuntimeError(
            "Aucun pack de langue Tesseract disponible. "
            "Installez au moins 'tesseract-lang' (fra) ou gardez 'eng'."
        )

    def _parse_measurements(self, text: str) -> List[PlanMeasurement]:
        return parse_measurements_from_text(text)
