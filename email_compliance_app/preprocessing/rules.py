def detect_category(text: str):
    t = text.lower()

    secrecy = any(k in t for k in [
        "confidential", "not public", "strictly between", "internal"
    ])
    trading = any(k in t for k in [
        "position", "trade", "enter", "adjust"
    ])

    if secrecy and trading:
        return "Secrecy + Market Manipulation"
    if secrecy:
        return "Secrecy"
    if any(k in t for k in ["volume", "price", "orders"]):
        return "Market Manipulation"
    if any(k in t for k in ["gift", "reward", "benefit"]):
        return "Market Bribery"
    if any(k in t for k in ["call", "offline", "verbal"]):
        return "Change in Communication"
    if any(k in t for k in ["complaint", "dissatisfied", "escalate"]):
        return "Complaints"
    if any(k in t for k in ["policy", "approval", "violate"]):
        return "Employee Ethics"

    return "General"


def detect_priority(category: str):
    if "Market Manipulation" in category or "Secrecy" in category:
        return "Critical"
    if "Bribery" in category or "Employee Ethics" in category:
        return "High"
    if "Change in Communication" in category:
        return "Medium"
    if "Complaints" in category:
        return "Low"
    return "Low"
