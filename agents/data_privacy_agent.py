
from agents.base_agent import BaseAgent

class DataPrivacyAgent(BaseAgent):
    def __init__(self):
        super().__init__("data_privacy_agent")

    def can_handle(self, task_type: str) -> bool:
        return task_type == "safeguard_data_check"

    def perform_task(self, data: dict, context: dict = None):
        candidate = data.get("candidate_data", {})
        
        if any(key in candidate for key in ["ssn", "credit_card", "password"]):
            return {"error": "PII detected — operation not allowed."}
        return {"status": "ok"}
