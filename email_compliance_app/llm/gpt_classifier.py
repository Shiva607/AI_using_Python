# Requires OPENAI_API_KEY set in environment
from openai import OpenAI
from models.llm_schema import LLMResult
import json
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPEN_ROUTER_API_KEY"),
)

from utils.normalizer import normalize_category, normalize_priority

def classify_with_gpt(cleaned_text, rule_category, rule_priority):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=150,
            messages=[
                {"role": "system", "content": "You are a compliance classification engine. Return JSON only."},
                {"role": "user", "content": json.dumps({
                    "cleaned_text": cleaned_text,
                    "rule_category": rule_category,
                    "rule_priority": rule_priority
                })}
            ]
        )

        result = json.loads(response.choices[0].message.content)

        return LLMResult(
            final_category=normalize_category(result["final_category"]),
            final_priority=normalize_priority(result["final_priority"])
        )

    except Exception:
        # 🔐 SAFE FALLBACK — NEVER PASS RAW VALUES
        return LLMResult(
            final_category=normalize_category(rule_category),
            final_priority=normalize_priority(rule_priority)
        )
