from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_db_session
from ..models import PlanRecord, PriceRequestRecord
from ..schemas import PriceRequestCreate, PriceRequestSchema, PriceResultSchema
from ..services.price_service import BackendPriceService

router = APIRouter(prefix="/plans/{plan_id}/prices", tags=["prices"])


def get_price_service() -> BackendPriceService:
    return BackendPriceService()


def _serialize_results(store_prices) -> List[PriceResultSchema]:
    return [
        PriceResultSchema(
            store=sp.store.name,
            title=sp.result.title if sp.result else "",
            link=sp.result.link if sp.result else "",
            price=sp.price.raw if sp.price else None,
            source=sp.source,
        )
        for sp in store_prices
    ]


@router.post("", response_model=PriceRequestSchema)
def request_prices(
    plan_id: int,
    payload: PriceRequestCreate,
    session: Session = Depends(get_db_session),
    price_service: BackendPriceService = Depends(get_price_service),
) -> PriceRequestSchema:
    plan = session.get(PlanRecord, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan introuvable.")

    query = payload.query or plan.dominant_label
    if not query:
        raise HTTPException(
            status_code=400,
            detail="Impossible de déduire une requête. Fournissez le champ 'query'.",
        )

    store_prices = price_service.lookup(query)
    record = PriceRequestRecord(
        plan_id=plan.id,
        query=query,
        results_json=BackendPriceService.serialize(store_prices),
    )
    session.add(record)
    session.commit()
    session.refresh(record)

    results = _serialize_results(store_prices)
    return PriceRequestSchema(
        id=record.id,
        plan_id=record.plan_id,
        query=record.query,
        created_at=record.created_at,
        results=results,
    )


@router.get("", response_model=List[PriceRequestSchema])
def list_price_requests(
    plan_id: int, session: Session = Depends(get_db_session)
) -> List[PriceRequestSchema]:
    plan = session.get(PlanRecord, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan introuvable.")
    price_requests = session.exec(
        select(PriceRequestRecord)
        .where(PriceRequestRecord.plan_id == plan_id)
        .order_by(PriceRequestRecord.created_at.desc())
    ).all()

    items: List[PriceRequestSchema] = []
    for record in price_requests:
        serialized = json.loads(record.results_json)
        results = [PriceResultSchema(**item) for item in serialized]
        items.append(
            PriceRequestSchema(
                id=record.id,
                plan_id=record.plan_id,
                query=record.query,
                created_at=record.created_at,
                results=results,
            )
        )
    return items
