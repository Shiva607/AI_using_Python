# email_compliance_app\preprocessing\cleaner.py

import re
from typing import Tuple, List

def preprocess_text(text: str) -> Tuple[str, str]:
    """
    Preprocess email text by removing junk and normalizing content.
    
    Args:
        text: Raw email body text
        
    Returns:
        Tuple of (cleaned_text, removed_items_summary)
    """
    removed = []
    original_text = text
    
    # 1. Remove URLs
    if re.search(r"https?://\S+|www\.\S+", text):
        removed.append("URLs")
    text = re.sub(r"https?://\S+|www\.\S+", " url ", text)
    
    # 2. Remove Email Addresses
    if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text):
        removed.append("email addresses")
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " email ", text)
    
    # 3. Remove Phone Numbers (multiple formats)
    phone_patterns = [
        r"\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",  # +1-555-123-4567, (555) 123-4567
        r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",  # 555-123-4567, 555.123.4567
        r"\b\d{10}\b"  # 5551234567
    ]
    for pattern in phone_patterns:
        if re.search(pattern, text):
            removed.append("phone numbers")
            text = re.sub(pattern, " number ", text)
            break
    
    # 4. Remove Dollar Amounts and Numbers with Currency Symbols
    if re.search(r"\$[\d,]+\.?\d*|\d+\s?(?:million|billion|thousand|crore|lakh)", text, re.IGNORECASE):
        removed.append("dollar amounts")
    text = re.sub(r"\$[\d,]+\.?\d*", " number ", text)
    text = re.sub(r"\d+\s?(?:million|billion|thousand|crore|lakh)", " number ", text, flags=re.IGNORECASE)
    
    # 5. Remove Account Numbers (with # prefix)
    if re.search(r"#\d+|Account[:\s]+\d+", text, re.IGNORECASE):
        removed.append("account numbers")
    text = re.sub(r"#\d+", " number ", text)
    text = re.sub(r"Account[:\s]+\d+", " number ", text, flags=re.IGNORECASE)
    
    # 6. Remove Dates (multiple formats)
    date_patterns = [
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",  # Jan 15, 2024
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",  # 15/01/2024, 01-15-24
        r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b"  # 2024-01-15
    ]
    for pattern in date_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            removed.append("dates")
            text = re.sub(pattern, " date ", text, flags=re.IGNORECASE)
            break
    
    # 7. Remove Time (12:30 PM, 14:30, etc.)
    if re.search(r"\b\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?\b", text):
        removed.append("time")
    text = re.sub(r"\b\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?\b", " time ", text)
    
    # 8. Remove Standalone Numbers
    if re.search(r"\b\d+\.?\d*\b", text):
        removed.append("numbers")
    text = re.sub(r"\b\d+\.?\d*\b", " number ", text)
    
    # 9. Check for Uppercase Words (before converting to lowercase)
    if re.search(r"\b[A-Z]{2,}\b", original_text):
        removed.append("uppercase words")
    
    # 10. Remove Excessive Punctuation
    if re.search(r"[!?]{2,}", original_text):
        removed.append("excessive punctuation")
    text = re.sub(r"[!?]{2,}", " ", text)
    
    # 11. Remove Emojis and Special Unicode Characters
    if re.search(r"[^\x00-\x7F]+", original_text):
        removed.append("emojis")
    text = re.sub(r"[^\x00-\x7F]+", " ", text)  # Remove non-ASCII
    
    # 12. Remove Special Characters (keep alphanumeric and spaces)
    if re.search(r"[^\w\s]", text):
        if "special characters" not in [r.split()[0] for r in removed]:
            removed.append("special characters")
    text = re.sub(r"[^\w\s]", " ", text)
    
    # 13. Remove Common Email Greetings
    greetings = [
        r"^(?:dear\s+sir/madam[,;]?\s*)",
        r"^(?:hi|hello|dear|hey|greetings)(?:\s+(?:team|all|there|everyone|colleague|sir|madam|friend))?\s*[,:]?\s*",
        r"^(?:good\s+(?:morning|afternoon|evening))\s*[,:]?\s*",
        r"^(?:hope\s+(?:this\s+)?(?:email\s+)?(?:finds\s+)?you(?:'re|\s+are)?\s+(?:well|doing\s+great))\s*[,.]?\s*"
    ]
    for pattern in greetings:
        if re.search(pattern, text, re.IGNORECASE):
            removed.append("greetings")
            text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
            break
    
    # 14. Remove Common Email Signatures/Closings
    closings = [
        r"(?:best|warm|kind|sincere)?\s*regards?\s*[,:]?.*$",
        r"(?:thanks?|thank\s+you|cheers|sincerely)[\s,]*.*$",
        r"(?:phone|tel|mobile|email|direct)[\s:]+.*$"
    ]
    for pattern in closings:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            if "signatures" not in removed:
                removed.append("signatures")
            text = re.sub(pattern, " ", text, flags=re.IGNORECASE | re.MULTILINE)
    
    # 15. Remove Disclaimer Text
    if re.search(r"disclaimer|confidential|privileged", text, re.IGNORECASE):
        removed.append("disclaimer")
    text = re.sub(r"disclaimer[:\s]+.*$", " ", text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"this\s+email.*(?:confidential|privileged).*", " ", text, flags=re.IGNORECASE)
    
    # 16. Remove Common Stop Words
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'but', 'by', 'for', 
        'from', 'has', 'have', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 
        'the', 'to', 'was', 'will', 'with', 'this', 'they', 'we', 'you', 'your',
        'i', 'me', 'my', 'our', 'us', 'their', 'there', 'can', 'could', 'would',
        'should', 'may', 'might', 'must', 'shall', 'am', 'do', 'does', 'did',
        'if', 'or', 'not', 'no', 'so', 'than', 'too', 'very', 'just', 'once'
    }
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove stop words
    words = text.split()
    original_word_count = len(words)
    words = [word for word in words if word not in stop_words and len(word) > 1]
    if len(words) < original_word_count:
        removed.append("stop words")
    
    # 17. Remove Extra Whitespace
    text = " ".join(words)
    text = re.sub(r"\s+", " ", text).strip()
    
    # Create summary of removed items
    removed_summary = ", ".join(sorted(set(removed))) if removed else "none"
    
    return text, removed_summary


def get_removed_items_list(text: str) -> List[str]:
    """
    Get a detailed list of what was removed during preprocessing.
    
    Args:
        text: Original email text
        
    Returns:
        List of removed item categories
    """
    _, summary = preprocess_text(text)
    return summary.split(", ") if summary != "none" else []


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_emails = [
        """Hi Team,
        
        The company's QUARTERLY numbers are MUCH STRONGER!!! than expected.
        Visit http://internal-news.bank.com for details.
        Contact me at trader@bank.com or call 555-1234.
        This is worth $5,000,000+ in potential gains!!!
        
        Best Regards,
        John Smith
        Phone: +1-555-1234
        """,
        
        """URGENT!!! Delete this email IMMEDIATELY!!! 🔥🔥
        Meeting at 3:30 PM on Jan 15, 2024.
        Account #12345 has $2,000,000 balance.
        """,
        
        """Dear Sir/Madam,
        
        Hope this email finds you well.
        I have concerns about transaction #98765.
        
        Thank you,
        Customer Service
        """
    ]
    
    print("=" * 80)
    print("EMAIL PREPROCESSING TEST RESULTS")
    print("=" * 80)
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}")
        print(f"{'='*80}")
        print(f"\nORIGINAL EMAIL:\n{email[:200]}...")
        
        cleaned, removed = preprocess_text(email)
        
        print(f"\n{'─'*80}")
        print(f"REMOVED ITEMS: {removed}")
        print(f"{'─'*80}")
        print(f"\nCLEANED TEXT:\n{cleaned}")
        print(f"\n{'='*80}\n")