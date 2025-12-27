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
# CONFIGURATION (Easy to tweak)
# --------------------------------------------------
WEIGHTS = {
    "category": 0.60,
    "confidence": 0.30,
    "language_risk": 0.10
}

# Category → Severity (0–5 scale) - cleaned, no duplicates
CATEGORY_SEVERITY = {
    "Secrecy": 5,
    "Market Manipulation": 4,
    "Market Manipulation / Misconduct": 4,
    "Market Bribery": 4,
    "Change in Communication": 3,
    "Complaints": 2,
    "Employee Ethics": 1,
}

# Score → Priority thresholds
SCORE_TO_PRIORITY = [
    (80, "Critical"),
    (65, "High"),
    (45, "Medium"),
    (0, "Low")  # default
]

def score_to_priority(score: float) -> str:
    for threshold, pri in SCORE_TO_PRIORITY:
        if score >= threshold:
            return pri
    return "Low"

def calculate_weighted_score(category_score: float, confidence: float, language_risk: float) -> float:
    """
    Final Score = 100 × (w_cat × normalized_category + w_conf × confidence + w_lang × language_risk)
    """
    norm_category = category_score / 5.0  # Normalize from 0–5 to 0–1
    weighted = (
        WEIGHTS["category"] * norm_category +
        WEIGHTS["confidence"] * confidence +
        WEIGHTS["language_risk"] * language_risk
    )
    return round(100 * weighted, 2)


def classify_with_gpt(cleaned_text: str, rule_category: str, rule_priority: str):
    """
    Uses LLM to detect categories, confidence, and language risk.
    Applies weighted scoring formula and returns final category, priority, and score.
    """
    try:
        prompt = f"""
You are a compliance risk scoring engine. Analyze the email and return ONLY valid JSON.

Email text:
{cleaned_text}

Rule-based suggestion:
Category: {rule_category}
Priority: {rule_priority}

INSTRUCTIONS:
1. Identify compliance risk categories present. Use ONLY these exact names:
   {', '.join(CATEGORY_SEVERITY.keys())}

2. Predefined severity for each:
   {json.dumps(CATEGORY_SEVERITY, indent=2)}

3. If multiple categories detected, average their severity scores.

4. Estimate:
   - model_confidence: Your confidence in category detection (0.0 to 1.0)
   - language_risk: How risky/evasive/inappropriate the language is (0.0 = neutral, 1.0 = highly risky)

5. Return JSON exactly like this:
{{
  "detected_categories": ["Category1", "Category2"],
  "average_severity": 3.5,
  "model_confidence": 0.85,
  "language_risk": 0.40
}}

EXAMPLE:
Email about insider tip + complaint tone → 
{{
  "detected_categories": ["Secrecy", "Complaints"],
  "average_severity": 3.5,
  "model_confidence": 0.92,
  "language_risk": 0.25
}}

Return ONLY JSON. No explanation.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)

        categories = result.get("detected_categories", [])
        avg_severity = float(result.get("average_severity", 0))
        confidence = float(result.get("model_confidence", 0.5))
        lang_risk = float(result.get("language_risk", 0.0))

        # Final category: top detected or fallback
        final_cat = categories[0] if categories else rule_category
        final_cat = normalize_category(final_cat)

        # Calculate final score
        score = calculate_weighted_score(avg_severity, confidence, lang_risk)
        final_pri = score_to_priority(score)

        # RETURN SCORE TOO — so you can show it in UI
        return LLMResult(
            final_category=final_cat,
            final_priority=normalize_priority(final_pri),
            score=score  # ← Now returning the calculated score
        )

    except Exception as e:
        print(f"LLM classification failed: {e}. Using rule-based fallback.")
        # Safe fallback
        return LLMResult(
            final_category=normalize_category(rule_category),
            final_priority=normalize_priority(rule_priority),
            score=0.0  # No score on fallback
        )