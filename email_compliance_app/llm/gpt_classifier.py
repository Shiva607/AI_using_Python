# llm/gpt_classifier.py

import json
import os
from openai import OpenAI
from models.llm_schema import LLMResult
from utils.normalizer import normalize_category, normalize_priority
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
)

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------
WEIGHTS = {
    "category": 0.60,
    "confidence": 0.30,
    "language_risk": 0.10
}

CATEGORY_SEVERITY = {
    "Secrecy": 5,
    "Market Manipulation": 4,
    "Market Manipulation / Misconduct": 4,
    "Market Bribery": 4,
    "Change in Communication": 3,
    "Complaints": 2,
    "Employee Ethics": 1,
}

SCORE_TO_PRIORITY = [
    (80, "Critical"),
    (65, "High"),
    (45, "Medium"),
    (0, "Low")
]

def score_to_priority(score: float) -> str:
    for threshold, pri in SCORE_TO_PRIORITY:
        if score >= threshold:
            return pri
    return "Low"

def calculate_weighted_score(category_score: float, confidence: float, language_risk: float) -> float:
    norm_category = category_score / 5.0
    weighted = (
        WEIGHTS["category"] * norm_category +
        WEIGHTS["confidence"] * confidence +
        WEIGHTS["language_risk"] * language_risk
    )
    return round(100 * weighted, 2)


def classify_with_gpt(cleaned_text: str, rule_category: str, rule_priority: str):
    """
    Uses few-shot prompting to make LLM follow the exact weighted scoring model.
    """
    try:
        prompt = f"""
You are a compliance risk scoring engine. You must return ONLY valid JSON in the exact format below.

Email text:
{cleaned_text}

Rule-based suggestion:
Category: {rule_category}
Priority: {rule_priority}

SEVERITY MAPPING (use exactly these values):
{json.dumps(CATEGORY_SEVERITY, indent=2)}

FORMULA:
Score = 100 × (0.60 × (average_severity / 5) + 0.30 × model_confidence + 0.10 × language_risk)

PRIORITY MAPPING:
≥80 → Critical
65–79 → High
45–64 → Medium
<45 → Low

FEW-SHOT EXAMPLES:

Example 1:
Email: Discussion about insider tip
Detected: ["Secrecy"]
Average severity: 5.0
Normalized: 1.00
Confidence: 0.90
Language risk: 0.40
Score: 100 × (0.60×1.00 + 0.30×0.90 + 0.10×0.40) = 91 → Critical

Example 2:
Email: Bribery offer + communication change
Detected: ["Market Bribery", "Change in Communication"]
Average severity: (4 + 3)/2 = 3.5
Normalized: 0.70
Confidence: 0.80
Language risk: 0.30
Score: 100 × (0.60×0.70 + 0.30×0.80 + 0.10×0.30) = 69 → High

Example 3:
Email: General complaint
Detected: ["Complaints"]
Average severity: 2.0
Normalized: 0.40
Confidence: 0.50
Language risk: 0.10
Score: 100 × (0.60×0.40 + 0.30×0.50 + 0.10×0.10) = 40 → Low

Example 4:
Email: Manipulation + Bribery
Detected: ["Market Manipulation", "Market Bribery"]
Average severity: 4.0
Normalized: 0.80
Confidence: 0.95
Language risk: 0.60
Score: 100 × (0.60×0.80 + 0.30×0.95 + 0.10×0.60) = 83 → Critical

NOW ANALYZE THE EMAIL ABOVE AND RETURN ONLY THIS JSON:
{{
  "detected_categories": ["Category1", "Category2"],
  "average_severity": 3.5,
  "model_confidence": 0.85,
  "language_risk": 0.40
}}
No explanation. Only JSON.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        # Safety checks
        if hasattr(response, 'error') and response.error:
            raise Exception(f"API Error: {response.error.message if hasattr(response.error, 'message') else str(response.error)}")
        
        if response.choices is None or len(response.choices) == 0:
            raise Exception("Empty response from API")

        raw = response.choices[0].message.content.strip()

        if any(word in raw.lower() for word in ["error", "invalid", "unauthorized", "authentication", "key", "not found"]):
            raise Exception(f"API returned error message: {raw}")

        result = json.loads(raw)

        categories = result.get("detected_categories", [])
        avg_severity = float(result.get("average_severity", 0))
        confidence = float(result.get("model_confidence", 0.5))
        lang_risk = float(result.get("language_risk", 0.0))

        final_cat = categories[0] if categories else rule_category
        final_cat = normalize_category(final_cat)

        score = calculate_weighted_score(avg_severity, confidence, lang_risk)
        final_pri = score_to_priority(score)

        return LLMResult(
            final_category=final_cat,
            final_priority=normalize_priority(final_pri),
            score=score,
            llm_success=True
        )

    except Exception as e:
        print(f"LLM classification failed: {e}")
        return LLMResult(
            final_category=normalize_category(rule_category),
            final_priority=normalize_priority(rule_priority),
            score=0.0,
            llm_success=False
        )