from fastapi import FastAPI
from datetime import datetime
from backend.baby_manager import BabyManager

app = FastAPI(title="Baby Manager API")
mgr = BabyManager()

__all__ = ["app"]  # Explicitly export app for ASGI

from pydantic import BaseModel

class FeedingRequest(BaseModel):
    milk_amount: int
    feeding_time: datetime | None = None

@app.post("/feeding")
async def record_feeding(request: FeedingRequest):
    mgr.record_feeding(request.milk_amount, request.feeding_time)
    return {"status": "Feeding recorded"}

@app.post("/sleep")
async def record_sleep(start_time: datetime, end_time: datetime):
    mgr.record_sleep(start_time, end_time)
    return {"status": "Sleep recorded"}

@app.post("/diaper")
async def record_diaper_change():
    mgr.record_diaper_change()
    return {"status": "Diaper change recorded"}

@app.get("/suggestions")
async def get_suggestions(current_time: datetime = None):
    return mgr.get_suggestions(current_time)

@app.post("/test/reset")
async def reset_test_data():
    mgr.last_feeding_time = None
    mgr.last_milk_amount = 0
    mgr.last_sleep_end = None
    mgr.last_diaper_change = None
    return {"status": "Test data reset"}
