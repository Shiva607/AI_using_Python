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

# Category → Severity (0–5 scale)
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
    Formula:
    Score = 100 × (w_cat × norm_cat + w_conf × confidence + w_lang × language_risk)
    """
    norm_category = category_score / 5.0  # Normalize 0–5 → 0–1
    weighted = (
        WEIGHTS["category"] * norm_category +
        WEIGHTS["confidence"] * confidence +
        WEIGHTS["language_risk"] * language_risk
    )
    return round(100 * weighted, 2)

def classify_with_gpt(cleaned_text: str, rule_category: str, rule_priority: str):
    """
    Calls LLM with detailed instructions for formula-based scoring.
    Returns LLMResult with final_category and final_priority.
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
1. Identify the main compliance risk categories present (use exact names from this list only):
   {', '.join(CATEGORY_SEVERITY.keys())}

2. For each detected category, assign its predefined severity:
   {json.dumps(CATEGORY_SEVERITY, indent=2)}

3. If multiple categories, average their severity scores.

4. Estimate:
   - model_confidence: How confident are you in your category assessment? (0.0 to 1.0)
   - language_risk: How aggressive, evasive, or inappropriate is the language? (0.0 = neutral, 1.0 = highly risky)

5. Return JSON in this exact format:
{{
  "detected_categories": ["Category1", "Category2"],  // empty list if none
  "average_severity": 3.5,                            // float, average of severity values
  "model_confidence": 0.85,                           // 0.0–1.0
  "language_risk": 0.40                               // 0.0–1.0
}}

EXAMPLE:
Input email talks about insider tip + mild complaint tone.

Response:
{{
  "detected_categories": ["Secrecy", "Complaints"],
  "average_severity": 3.5,
  "model_confidence": 0.92,
  "language_risk": 0.25
}}

Return ONLY the JSON. No explanation.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)

        # Extract values
        categories = result.get("detected_categories", [])
        avg_severity = float(result.get("average_severity", 0))
        confidence = float(result.get("model_confidence", 0.5))
        lang_risk = float(result.get("language_risk", 0.0))

        # Final category: use LLM's top one, or fallback to rule
        final_cat = categories[0] if categories else rule_category
        final_cat = normalize_category(final_cat)

        # Calculate score
        score = calculate_weighted_score(avg_severity, confidence, lang_risk)
        final_pri = score_to_priority(score)

        return LLMResult(
            final_category=final_cat,
            final_priority=normalize_priority(final_pri)
        )

    except Exception as e:
        # SAFE FALLBACK — Use rule-based only
        print(f"LLM classification failed: {e}. Using rule-based fallback.")
        return LLMResult(
            final_category=normalize_category(rule_category),
            final_priority=normalize_priority(rule_priority)
        )