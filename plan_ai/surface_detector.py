from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import cv2  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    cv2 = None  # type: ignore

from shared.utils import require_dependency


@dataclass
class DetectedSurface:
    contour_area_px: float
    bounding_box: Tuple[int, int, int, int]


def detect_surfaces_from_image(
    image_path: str | Path, *, min_area_px: int = 10_000
) -> List[DetectedSurface]:
    """Detects large closed contours that may represent rooms or zones."""
    require_dependency(cv2, "opencv-python")

    img_path = Path(image_path)
    frame = cv2.imread(str(img_path))
    if frame is None:
        raise RuntimeError(f"Impossible de charger l'image {img_path}")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected: List[DetectedSurface] = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area_px:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        detected.append(DetectedSurface(contour_area_px=area, bounding_box=(x, y, w, h)))

    return detected
