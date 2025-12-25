ALLOWED_CATEGORIES = {
    "Secrecy",
    "Market Manipulation",
    "Market Bribery",
    "Change in Communication",
    "Complaints",
    "Employee Ethics",
    "Secrecy + Market Manipulation",
    "Market Bribery + Employee Ethics",
}

def normalize_category(category: str) -> str:
    if category not in ALLOWED_CATEGORIES:
        # safest default for ambiguity
        return "Employee Ethics"
    return category


def normalize_priority(priority: str) -> str:
    if priority not in {"Critical", "High", "Medium", "Low"}:
        return "Low"
    return priority
