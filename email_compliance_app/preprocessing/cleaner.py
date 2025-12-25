import re

def preprocess_text(text: str):
    removed = []

    if re.search(r"http\S+", text):
        removed.append("URL")
    text = re.sub(r"http\S+", "", text)

    if re.search(r"\S+@\S+", text):
        removed.append("email IDs")
    text = re.sub(r"\S+@\S+", "email", text)

    if re.search(r"\d{3}-\d{4}", text):
        removed.append("phone number")
    text = re.sub(r"\d{3}-\d{4}", "number", text)

    if re.search(r"\$\d[\d,]*", text):
        removed.append("dollar amount")
    text = re.sub(r"\$\d[\d,]*", "number", text)

    if re.search(r"[^\w\s]", text):
        removed.append("emojis")
    text = re.sub(r"[^\w\s]", " ", text)

    if re.search(r"\b[A-Z]{3,}\b", text):
        removed.append("uppercase words")

    if "!!!" in text:
        removed.append("!!! punctuation")
        text = text.replace("!!!", "")

    removed.append("greeting & signature")

    cleaned = " ".join(text.lower().split())
    return cleaned, ", ".join(sorted(set(removed)))
