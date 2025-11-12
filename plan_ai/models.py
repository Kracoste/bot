from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class PlanMeasurement:
    label: str
    area_m2: Optional[float] = None
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    source: str = "text"


@dataclass
class PlanAnalysis:
    source: Path
    measurements: List[PlanMeasurement] = field(default_factory=list)
    raw_text: str = ""
