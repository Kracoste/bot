from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from .models import PlanMeasurement


@dataclass
class SurfaceSummary:
    total_area_m2: float
    total_length_m: float
    measurement_count: int
    dominant_label: Optional[str]


def summarize_measurements(measurements: List[PlanMeasurement]) -> SurfaceSummary:
    areas = [m.area_m2 for m in measurements if m.area_m2 is not None]
    lengths = [m.length_m for m in measurements if m.length_m is not None]

    total_area = sum(areas) if areas else 0.0
    total_length = sum(lengths) if lengths else 0.0
    dominant_label = None
    if areas:
        dominant_measurement = max(
            (m for m in measurements if m.area_m2 is not None),
            key=lambda m: m.area_m2 or 0.0,
        )
        dominant_label = dominant_measurement.label

    return SurfaceSummary(
        total_area_m2=total_area,
        total_length_m=total_length,
        measurement_count=len(measurements),
        dominant_label=dominant_label,
    )


def measurements_to_dataframe(measurements: List[PlanMeasurement]) -> pd.DataFrame:
    records = [
        {
            "label": m.label,
            "area_m2": m.area_m2,
            "length_m": m.length_m,
            "width_m": m.width_m,
        }
        for m in measurements
    ]
    return pd.DataFrame.from_records(records, columns=["label", "area_m2", "length_m", "width_m"])


def estimate_material_requirements(
    measurements: List[PlanMeasurement], *, coverage_per_unit_m2: float = 1.0
) -> Dict[str, float]:
    """Rough estimation of material quantities based on surface coverage."""
    if coverage_per_unit_m2 <= 0:
        raise ValueError("coverage_per_unit_m2 doit être > 0")

    total_area = sum(m.area_m2 for m in measurements if m.area_m2 is not None)
    return {
        "total_area_m2": total_area,
        "estimated_units": total_area / coverage_per_unit_m2 if total_area else 0.0,
    }
