# models/email_schema.py

from pydantic import BaseModel, Field
from typing import Literal

class EmailOutput(BaseModel):
    """
    Schema for the final processed email output.
    Used for UI display, table, and Excel export.
    """
    unique_id: int = Field(..., description="Unique identifier from input Excel")
    from_email: str = Field(..., description="Sender email address")
    to_email: str = Field(..., description="Recipient email address(es)")
    subject: str = Field(..., description="Email subject line")
    email_body: str = Field(..., description="Original raw email body (with junk)")
    junk_removed: str = Field(..., description="Summary of removed noise (URLs, emails, emojis, etc.)")
    cleaned_text: str = Field(..., description="Cleaned email body after preprocessing")
    category: str = Field(..., description="Final compliance risk category")
    priority: Literal["Critical", "High", "Medium", "Low"] = Field(..., description="Final risk priority level")
    score: float = Field(0.0, description="Weighted risk score (0-100) from formula")  # ← NEW: Risk Score
    llm_success: bool = True


    class Config:
        # Allows extra fields if needed in future
        extra = "forbid"
        # Nice field names in JSON/Excel
        allow_population_by_field_name = True