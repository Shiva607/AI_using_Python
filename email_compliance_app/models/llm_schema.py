# email_compliance_app\models\llm_schema.py

from pydantic import BaseModel
from typing import Literal

class LLMResult(BaseModel):
    final_category: Literal[
        "Secrecy",
        "Market Manipulation",
        "Market Bribery",
        "Change in Communication",
        "Complaints",
        "Employee Ethics",
        "Secrecy + Market Manipulation",
        "Market Bribery + Employee Ethics"
    ]
    final_priority: Literal["Critical", "High", "Medium", "Low"]
    score: float = 0.0  # ← New field: the calculated risk score (0–100)
    llm_success: bool = True
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0 