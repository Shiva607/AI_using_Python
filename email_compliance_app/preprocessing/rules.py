# preprocessing/rules.py

def detect_category(text: str) -> str:
    t = text.lower()

    # 1. Secrecy - strong indicators
    secrecy_keywords = [
        "confidential", "strictly between us", "do not share", "keep this private",
        "off the record", "between us", "don't tell", "internal only", "not public",
        "delete after reading", "destroy this", "burn after reading"
    ]
    if any(k in t for k in secrecy_keywords):
        return "Secrecy"

    # 2. Market Manipulation - trading signals
    manipulation_keywords = [
        "position your trades", "front run", "pump", "dump", "move the price",
        "coordinate", "timing is important", "before announcement", "take advantage",
        "adjust position", "enter now", "load up", "get in before"
    ]
    if any(k in t for k in manipulation_keywords):
        return "Market Manipulation"

    # 3. Market Bribery
    bribery_keywords = [
        "gift", "favor", "kickback", "reward", "incentive", "benefit in return",
        "something for you", "gratitude", "compensation", "arrangement"
    ]
    if any(k in t for k in bribery_keywords):
        return "Market Bribery"

    # 4. Change in Communication
    comm_change_keywords = [
        "call me", "let's discuss offline", "verbal", "in person", "not in email",
        "delete this", "switch to phone", "avoid writing"
    ]
    if any(k in t for k in comm_change_keywords):
        return "Change in Communication"

    # 5. Complaints - strong dissatisfaction
    complaint_keywords = [
        "complaint", "dissatisfied", "unacceptable", "escalate", "regulator",
        "not resolved", "lost money", "poor execution", "worst", "immediately"
    ]
    if any(k in t for k in complaint_keywords):
        return "Complaints"

    # 6. Employee Ethics / Policy Violation
    ethics_keywords = [
        "policy", "violate", "approval", "not allowed", "against rules",
        "bypass", "exception", "special case", "don't check with compliance"
    ]
    if any(k in t for k in ethics_keywords):
        return "Employee Ethics"

    # Default
    return "General"


def detect_priority(category: str, text: str = "") -> str:
    """
    Improved priority: uses category + tone intensity
    """
    t = text.lower()

    # Critical: Secrecy or Manipulation (highest risk)
    if "Secrecy" in category or "Market Manipulation" in category:
        return "Critical"

    # High: Bribery, Ethics violations, or strong angry complaints
    if "Market Bribery" in category or "Employee Ethics" in category:
        return "High"

    if "Complaints" in category:
        # Strong complaints → High, mild → Medium
        strong_words = ["extremely", "furious", "outraged", "escalate", "regulator", "lawyer", "lost money"]
        if any(w in t for w in strong_words):
            return "High"
        return "Medium"

    if "Change in Communication" in category:
        return "Medium"

    return "Low"