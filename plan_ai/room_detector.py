from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore
    np = None  # type: ignore

from shared.utils import require_dependency


@dataclass
class RoomDetection:
    area_px: float
    bounding_box: Tuple[int, int, int, int]


class RoomDetector:
    def __init__(self, *, min_area_px: int = 5_000) -> None:
        self.min_area_px = min_area_px

    def detect(self, path: Path) -> List[RoomDetection]:
        require_dependency(cv2, "opencv-python")
        frame = cv2.imread(str(path))
        if frame is None:
            return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
        edges = cv2.Canny(blurred, threshold1=50, threshold2=150)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections: List[RoomDetection] = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area_px:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            detections.append(RoomDetection(area_px=float(area), bounding_box=(x, y, w, h)))
        return detections
