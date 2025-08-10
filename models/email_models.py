from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class EmailMessage(BaseModel):
    """Represents a single email message."""
    to: str = Field(..., description="The primary recipient's email address.")
    subject: str
    body: str
    format: Literal["text", "html"] = "text"
    cc: Optional[List[str]] = Field(None, description="List of CC recipients.")
    bcc: Optional[List[str]] = Field(None, description="List of BCC recipients.")

class BulkEmailRequest(BaseModel):
    """Request model for sending multiple emails."""
    emails: List[EmailMessage]
    batch_size: int = Field(10, description="Number of emails to send per batch for rate limiting.")
    delay_between_batches: float = Field(1.0, description="Delay in seconds between batches.")

class EmailSendResult(BaseModel):
    """Result for a single email sent in a bulk operation."""
    email_index: int
    success: bool
    recipient: str
    message_id: Optional[str] = None
    error: Optional[str] = None

class BulkEmailResponse(BaseModel):
    """The response format for the bulk email sending tool."""
    total_emails: int
    successful: int
    failed: int
    results: List[EmailSendResult]

class QuotaStatus(BaseModel):
    """Represents the current Gmail API quota status."""
    current_usage: int
    limit: int
    reset_time: Optional[str] = None