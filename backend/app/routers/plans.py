from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.params import Form
from sqlmodel import Session, select

from ..config import UPLOAD_DIR
from ..database import get_db_session
from ..models import PlanRecord, PriceRequestRecord
from ..schemas import (
    MeasurementSchema,
    PlanCreateResponse,
    PlanDetailSchema,
    PlanSummarySchema,
)
from ..services.plan_service import PlanService

router = APIRouter(prefix="/plans", tags=["plans"])


def get_plan_service() -> PlanService:
    return PlanService()


def _deserialize_measurements(raw: str) -> List[MeasurementSchema]:
    data = json.loads(raw)
    return [MeasurementSchema(**item) for item in data]


@router.post(
    "",
    response_model=PlanCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_plan(
    *,
    file: UploadFile = File(...),
    coverage: float = Form(1.0),
    session: Session = Depends(get_db_session),
    plan_service: PlanService = Depends(get_plan_service),
) -> PlanCreateResponse:
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".pdf", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(status_code=400, detail="Format supporté: PDF, PNG, JPG.")

    temp_path = UPLOAD_DIR / f"{file.filename}"
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        analysis, data = plan_service.analyze_plan(temp_path, coverage)
    except RuntimeError as exc:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    summary = data["summary"]
    estimation = data["estimation"]

    record = PlanRecord(
        filename=file.filename,
        stored_path=str(temp_path),
        measurement_count=summary.measurement_count,
        total_area_m2=summary.total_area_m2,
        total_length_m=summary.total_length_m,
        dominant_label=summary.dominant_label,
        measurements_json=plan_service.measurements_to_json(analysis.measurements),
    )
    session.add(record)
    session.commit()
    session.refresh(record)

    measurements = [MeasurementSchema(**m.__dict__) for m in analysis.measurements]
    return PlanCreateResponse(
        id=record.id,
        filename=record.filename,
        created_at=record.created_at,
        measurement_count=record.measurement_count,
        total_area_m2=record.total_area_m2,
        total_length_m=record.total_length_m,
        dominant_label=record.dominant_label,
        measurements=measurements,
        estimation_total_area_m2=estimation["total_area_m2"],
        estimation_units=estimation["estimated_units"],
    )


@router.get("", response_model=List[PlanSummarySchema])
def list_plans(session: Session = Depends(get_db_session)) -> List[PlanSummarySchema]:
    plans = session.exec(select(PlanRecord).order_by(PlanRecord.created_at.desc())).all()
    return [
        PlanSummarySchema(
            id=plan.id,
            filename=plan.filename,
            created_at=plan.created_at,
            measurement_count=plan.measurement_count,
            total_area_m2=plan.total_area_m2,
            total_length_m=plan.total_length_m,
            dominant_label=plan.dominant_label,
        )
        for plan in plans
    ]


@router.get("/{plan_id}", response_model=PlanDetailSchema)
def get_plan(plan_id: int, session: Session = Depends(get_db_session)) -> PlanDetailSchema:
    plan = session.get(PlanRecord, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan introuvable.")
    measurements = _deserialize_measurements(plan.measurements_json)
    return PlanDetailSchema(
        id=plan.id,
        filename=plan.filename,
        created_at=plan.created_at,
        measurement_count=plan.measurement_count,
        total_area_m2=plan.total_area_m2,
        total_length_m=plan.total_length_m,
        dominant_label=plan.dominant_label,
        measurements=measurements,
    )
