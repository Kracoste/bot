from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

from plan_ai.geometry_calculator import (
    estimate_material_requirements,
    summarize_measurements,
)
from plan_ai.plan_reader import PlanAnalysis, PlanReader
from plan_ai.room_detector import RoomDetector
from plan_ai.models import PlanMeasurement
from shared.utils import log_info


class PlanService:
    def __init__(self) -> None:
        self.reader = PlanReader()
        self.detector = RoomDetector()

    def analyze_plan(self, plan_path: Path, coverage: float) -> Tuple[PlanAnalysis, dict]:
        analysis = self.reader.read(plan_path)
        analysis.measurements.extend(
            self._augment_with_room_detection(analysis, plan_path)
        )
        summary = summarize_measurements(analysis.measurements)
        estimation = estimate_material_requirements(
            analysis.measurements, coverage_per_unit_m2=max(coverage, 0.1)
        )
        log_info(
            f"Plan analysé: {plan_path.name} | mesures={summary.measurement_count} | "
            f"surface={summary.total_area_m2:.2f} m²"
        )
        return analysis, {
            "summary": summary,
            "estimation": estimation,
        }

    @staticmethod
    def measurements_to_json(measurements: List[PlanMeasurement]) -> str:
        return json.dumps(
            [
                {
                    "label": m.label,
                    "area_m2": m.area_m2,
                    "length_m": m.length_m,
                    "width_m": m.width_m,
                    "source": m.source,
                }
                for m in measurements
            ],
            ensure_ascii=False,
        )

    def _augment_with_room_detection(
        self, analysis: PlanAnalysis, plan_path: Path
    ) -> List[PlanMeasurement]:
        if plan_path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            return []

        rooms = self.detector.detect(plan_path)
        if not rooms:
            return []

        text_area = sum(m.area_m2 or 0 for m in analysis.measurements if m.area_m2)
        total_px = sum(room.area_px for room in rooms)
        scale = (text_area / total_px) if text_area and total_px else None

        augmented: List[PlanMeasurement] = []
        for idx, room in enumerate(sorted(rooms, key=lambda r: r.area_px, reverse=True), 1):
            area_m2 = room.area_px * scale if scale else None
            length_guess = (area_m2 ** 0.5) if area_m2 else None
            augmented.append(
                PlanMeasurement(
                    label=f"Zone détectée #{idx}",
                    area_m2=area_m2,
                    length_m=length_guess,
                    width_m=length_guess,
                    source="vision",
                )
            )
        return augmented
