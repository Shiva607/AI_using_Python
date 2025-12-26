from typing import Set

# --------------------------------------------------
# ALLOWED CATEGORIES (Exact matches required from LLM or rules)
# --------------------------------------------------
ALLOWED_CATEGORIES: Set[str] = {
    "Secrecy",
    "Market Manipulation",
    "Market Bribery",
    "Change in Communication",
    "Complaints",
    "Employee Ethics",
    "Secrecy + Market Manipulation",
    "Market Bribery + Employee Ethics",
}

# --------------------------------------------------
# ALLOWED PRIORITIES
# --------------------------------------------------
ALLOWED_PRIORITIES: Set[str] = {
    "Critical",
    "High",
    "Medium",
    "Low"
}

# --------------------------------------------------
# NORMALIZATION FUNCTIONS
# --------------------------------------------------
def normalize_category(category: str) -> str:
    """
    Normalize the detected category.
    - Strips whitespace
    - Ensures exact match against ALLOWED_CATEGORIES
    - Falls back to safest default: "Employee Ethics" (lowest risk)
    """
    if not category:
        return "Employee Ethics"

    cleaned = category.strip()

    if cleaned in ALLOWED_CATEGORIES:
        return cleaned

    # Optional: Add fuzzy tolerance later if needed (e.g., case-insensitive)
    # For now: strict match for safety and consistency
    return "Employee Ethics"


def normalize_priority(priority: str) -> str:
    """
    Normalize the priority level.
    - Strips whitespace
    - Ensures exact match against allowed values
    - Falls back to "Low" (safest)
    """
    if not priority:
        return "Low"

    cleaned = priority.strip()

    if cleaned in ALLOWED_PRIORITIES:
        return cleaned

    return "Low"


# --------------------------------------------------
# OPTIONAL: Helper to validate multiple categories
# --------------------------------------------------
def normalize_categories(categories: list[str]) -> list[str]:
    """
    Normalize a list of categories (e.g., from LLM detecting multiple).
    Returns only valid ones.
    """
    if not categories:
        return []

    valid = [normalize_category(cat) for cat in categories if normalize_category(cat) != "Employee Ethics"]
    # If all invalid, return empty or fallback
    return valid if valid else []