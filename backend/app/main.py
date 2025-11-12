from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from plan_ai import plan_reader  # noqa: F401

from .config import ALLOWED_ORIGINS
from .database import init_db
from .routers import plans, prices

app = FastAPI(title="Plan & Prix API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(plans.router)
app.include_router(prices.router)
