from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

class BabyActivity(BaseModel):
    timestamp: datetime
    type: str  # "feeding", "sleep", "diaper"
    details: Dict

class BabyInfo(BaseModel):
    gender: str = "unknown"
    birthday: datetime = datetime.now()
    weight_kg: float = 3.5

class BabyManager:
    def __init__(self, baby_info: BabyInfo = BabyInfo()):
        self.baby_info = baby_info
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

        self.has_any_records = False

    def _check_records_exist(self):
        """Check if any records exist for any activity type"""
        return any([
            self.last_feeding_time,
            self.last_sleep_end,
            self.last_diaper_change
        ])

    def get_suggestions(self, current_time: datetime = None):
        """Generate AI-powered care suggestions using ChatGPT"""
        if not self._check_records_exist():
            return {"message": "Please provide initial baby care records to enable suggestions."}
        from openai import OpenAI
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

        prompt = f"""Baby care history:
        Last feeding: {self.last_feeding_time.strftime('%Y-%m-%d %H:%M') if self.last_feeding_time else 'Never'}
        Last milk amount: {self.last_milk_amount}ml
        Last sleep ended: {self.last_sleep_end.strftime('%Y-%m-%d %H:%M') if self.last_sleep_end else 'Never'}
        Last diaper change: {self.last_diaper_change.strftime('%Y-%m-%d %H:%M') if self.last_diaper_change else 'Never'}

        Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        Generate ONLY 3 suggestions following EXACTLY these rules:
        1. Start with emoji (🍼🛌💧)
        2. Max 10 words
        3. Include time reference using "Xh ago" or "Never"
        4. Strict format: [emoji] [Action] - [Time reference]
        5. No introductory text
        
        Examples when no history:
        🍼 Feed 30-60ml milk - Never fed
        🛌 Start bedtime routine - Never slept
        💧 Change diaper now - Never changed
        
        Examples with history:
        🍼 Feed 60-90ml milk - Last feeding 3h ago
        🛌 Start nap routine - Awake 2h 45m
        💧 Check diaper status - Last change 4h ago
        
        Current status:
        Last feeding: {self.last_feeding_time.strftime('%Y-%m-%d %H:%M') if self.last_feeding_time else 'Never'}
        Last sleep: {self.last_sleep_end.strftime('%Y-%m-%d %H:%M') if self.last_sleep_end else 'Never'}
        Last diaper: {self.last_diaper_change.strftime('%Y-%m-%d %H:%M') if self.last_diaper_change else 'Never'}"""
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=150
            )
            
            # Parse and validate suggestions
            raw_suggestions = response.choices[0].message.content.split("\n")
            validated = []
            
            for s in raw_suggestions:
                s = s.strip()
                if not s:
                    continue
                # Enforce emoji rules
                emoji_map = {
                    "feed": "🍼",
                    "milk": "🍼",
                    "sleep": "🛌",
                    "nap": "🛌",
                    "diaper": "💧",
                    "change": "💧"
                }
                
                # Remove any existing emoji and whitespace
                s = s.lstrip("🛌💧🍼👶").strip()
                
                # Find matching emoji
                emoji = "👶"
                for key, value in emoji_map.items():
                    if key in s.lower():
                        emoji = value
                        break
                        
                # Split on first hyphen only and enforce format
                parts = s.split('-', 1)
                # Clean hyphens only in the action part
                action = parts[0].strip().replace(' - ', '-') if len(parts) > 0 else s.strip()
                time_ref = parts[1].strip() if len(parts) > 1 else "Time unknown"
                s = f"{emoji} {action} - {time_ref}"
                validated.append(s[:100])
                
            return {"suggestions": validated[:3]}  # Return max 3
        except Exception as e:
            return {"error": str(e)}
