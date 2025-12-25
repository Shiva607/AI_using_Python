from pydantic import BaseModel
from typing import Literal

class EmailOutput(BaseModel):
    unique_id: int
    from_email: str
    to_email: str
    subject: str
    email_body: str
    category: str
    priority: Literal["Critical", "High", "Medium", "Low"]
    junk_removed: str
    cleaned_text: str
