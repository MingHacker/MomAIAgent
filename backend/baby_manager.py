from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel

class BabyActivity(BaseModel):
    timestamp: datetime
    type: str  # "feeding", "sleep", "diaper"
    details: Dict

class BabyManager:
    def __init__(self):
        self.activities: List[BabyActivity] = []
        self.last_feeding_time: Optional[datetime] = None
        self.last_milk_amount: int = 0
        self.last_sleep_end: Optional[datetime] = None
        self.last_diaper_change: Optional[datetime] = None

    def record_feeding(self, milk_amount: int, feeding_time: datetime = None):
        time = feeding_time or datetime.now()
        self.activities.append(BabyActivity(
            timestamp=time,
            type="feeding",
            details={"amount_ml": milk_amount}
        ))
        self.last_feeding_time = time
        self.last_milk_amount = milk_amount

    def record_sleep(self, start_time: datetime, end_time: datetime):
        self.activities.append(BabyActivity(
            timestamp=start_time,
            type="sleep",
            details={"end_time": end_time, "duration_min": (end_time - start_time).seconds // 60}
        ))
        self.last_sleep_end = end_time

    def record_diaper_change(self, change_time: datetime = None):
        time = change_time or datetime.now()
        self.activities.append(BabyActivity(
            timestamp=time,
            type="diaper",
            details={}
        ))
        self.last_diaper_change = time

    def should_feed(self, current_time: datetime = None) -> bool:
        current_time = current_time or datetime.now()
        if not self.last_feeding_time:
            return True
        elapsed = current_time - self.last_feeding_time
        if elapsed > timedelta(hours=3):
            return True
        if self.last_milk_amount <= 100 and elapsed > timedelta(hours=2):
            return True
        return False

    def should_sleep(self, current_time: datetime = None) -> bool:
        current_time = current_time or datetime.now()
        if not self.last_sleep_end:
            return False  # Don't suggest sleep if no history
        elapsed = current_time - self.last_sleep_end
        return elapsed > timedelta(hours=2)

    def should_change_diaper(self, current_time: datetime = None) -> bool:
        current_time = current_time or datetime.now()
        if not self.last_diaper_change:
            return False  # Don't suggest change if no history
        elapsed = current_time - self.last_diaper_change
        return elapsed > timedelta(hours=2)

    def get_suggestions(self, current_time: datetime = None):
        return {
            "feed": self.should_feed(),
            "sleep": self.should_sleep(),
            "change_diaper": self.should_change_diaper()
        }
