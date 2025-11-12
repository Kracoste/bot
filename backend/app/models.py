from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PlanRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    stored_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    measurement_count: int
    total_area_m2: float
    total_length_m: float
    dominant_label: Optional[str] = None
    measurements_json: str


class PriceRequestRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="planrecord.id")
    query: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    results_json: str
