from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MeasurementSchema(BaseModel):
    label: str
    area_m2: Optional[float] = None
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    source: Optional[str] = None


class PlanSummarySchema(BaseModel):
    id: int
    filename: str
    created_at: datetime
    measurement_count: int
    total_area_m2: float
    total_length_m: float
    dominant_label: Optional[str]


class PlanDetailSchema(PlanSummarySchema):
    measurements: List[MeasurementSchema]


class PlanCreateResponse(PlanDetailSchema):
    estimation_total_area_m2: float
    estimation_units: float


class PriceResultSchema(BaseModel):
    store: str
    title: str
    link: str
    price: Optional[str]
    source: str


class PriceRequestSchema(BaseModel):
    id: int
    plan_id: int
    query: str
    created_at: datetime
    results: List[PriceResultSchema]


class PriceRequestCreate(BaseModel):
    query: Optional[str] = None
