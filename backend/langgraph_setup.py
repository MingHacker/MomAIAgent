from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from datetime import datetime
from .baby_manager import BabyManager, BabyActivity

class BabyState(TypedDict):
    activities: List[BabyActivity]
    last_input: str
    manager: BabyManager
    response: str

def create_baby_workflow():
    manager = BabyManager()
    workflow = StateGraph(BabyState)
    
    # Define nodes
    def record_feeding(state: BabyState):
        parts = state["last_input"].split()
        amount = int(parts[0])
        manager.record_feeding(amount)
        return {"response": f"✅ Feeding recorded: {amount}ml"}

    def record_sleep(state: BabyState):
        # Would parse start/end times from input
        manager.record_sleep(datetime.now(), datetime.now())
        return {"response": "✅ Sleep recorded"}

    def record_diaper(state: BabyState):
        manager.record_diaper_change()
        return {"response": "✅ Diaper change recorded"}

    def check_suggestions(state: BabyState):
        suggestions = []
        if manager.should_feed():
            suggestions.append("🕒 Time to feed")
        if manager.should_sleep():
            suggestions.append("🛌 Time for sleep")
        if manager.should_change_diaper():
            suggestions.append("👶 Check diaper")
        return {"response": "\n".join(suggestions) or "All good!"}

    # Add nodes
    workflow.add_node("record_feeding", record_feeding)
    workflow.add_node("record_sleep", record_sleep)
    workflow.add_node("record_diaper", record_diaper)
    workflow.add_node("suggest_actions", check_suggestions)

    # Set entry point
    workflow.set_entry_point("suggest_actions")

    # Add edges
    workflow.add_edge("record_feeding", "suggest_actions")
    workflow.add_edge("record_sleep", "suggest_actions")
    workflow.add_edge("record_diaper", "suggest_actions")
    workflow.add_edge("suggest_actions", END)

    return workflow.compile()
