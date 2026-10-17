
import os
from collections import defaultdict

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)

API_KEY = os.environ.get("API_KEY", "")
EMAIL = os.environ.get("EMAIL", "")


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: list[Event]


@app.post("/analytics")
def analytics(
    body: AnalyticsRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_totals = defaultdict(float)
    revenue = 0.0

    for event in body.events:
        if event.amount > 0:
            revenue += event.amount
            user_totals[event.user] += event.amount

    top_user = (
        max(user_totals, key=user_totals.get)
        if user_totals else None
    )

    return {
        "email": EMAIL,
        "total_events": len(body.events),
        "unique_users": len({e.user for e in body.events}),
        "revenue": revenue,
        "top_user": top_user,
    }


@app.get("/")
def home():
    return {"status": "ok", "endpoint": "/analytics"}
