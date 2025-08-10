import time
from typing import List

from fastmcp.server import FastMCP
from ..services.gmail_client import GmailClient
from ..models.email_models import (
    BulkEmailRequest,
    BulkEmailResponse,
    EmailMessage,
    EmailSendResult,
    QuotaStatus,
)

mcp = FastMCP()

def get_gmail_client():
    """Helper function to instantiate the Gmail client."""
    # In a more advanced setup, this could use dependency injection.
    return GmailClient()

@mcp.tool()
def send_single_email(email: EmailMessage) -> EmailSendResult:
    """
    Sends a single email using the Gmail API.

    Args:
        email: The email message to send.

    Returns:
        The result of the send operation.
    """
    client = get_gmail_client()
    result = client.send_email(email)
    
    if 'error' in result:
        return EmailSendResult(
            email_index=0,
            success=False,
            recipient=email.to,
            error=result['error']
        )
    else:
        return EmailSendResult(
            email_index=0,
            success=True,
            recipient=email.to,
            message_id=result.get('id')
        )

@mcp.tool()
def send_multiple_emails(request: BulkEmailRequest) -> BulkEmailResponse:
    """
    Sends multiple emails in batches using the Gmail API.

    Args:
        request: A request object containing a list of emails and batching options.

    Returns:
        A response object with the results of each email send operation.
    """
    client = get_gmail_client()
    results: List[EmailSendResult] = []
    successful_sends = 0
    failed_sends = 0

    for i, email in enumerate(request.emails):
        if i > 0 and i % request.batch_size == 0:
            time.sleep(request.delay_between_batches)

        send_result = client.send_email(email)

        if 'error' in send_result:
            failed_sends += 1
            results.append(EmailSendResult(
                email_index=i,
                success=False,
                recipient=email.to,
                error=send_result['error']
            ))
        else:
            successful_sends += 1
            results.append(EmailSendResult(
                email_index=i,
                success=True,
                recipient=email.to,
                message_id=send_result.get('id')
            ))

    return BulkEmailResponse(
        total_emails=len(request.emails),
        successful=successful_sends,
        failed=failed_sends,
        results=results
    )

@mcp.tool()
def get_email_quota_status() -> QuotaStatus:
    """
    Checks the current Gmail API quota usage and limits.
    
    Note: The standard Gmail API does not provide a direct programmatic way to check
    real-time quota usage. This tool returns static information based on general
    Gmail limits and does not reflect live data.
    """
    client = get_gmail_client()
    # The client returns a dictionary that we use to populate the Pydantic model.
    # A mock response is used since the API doesn't support this directly.
    status_dict = client.get_quota_status()
    
    # A real implementation would need to parse the response more carefully.
    # For this mock, we assume the client returns data that fits the model.
    # For example: {'current_usage': 0, 'limit': 500, 'reset_time': '...'}
    # We will assume the client returns a dictionary that can be unpacked into the model.
    # A more robust solution would handle potential mismatches.
    try:
        # Let's assume the client returns a dict with 'current_usage', 'limit', 'reset_time'
        # and we'll make them fit the model.
        mock_status = {
            "current_usage": 0, # Placeholder
            "limit": 500, # Standard limit
            "reset_time": "Daily reset (not live data)"
        }
        return QuotaStatus(**mock_status)
    except TypeError:
        # Fallback if the client's response doesn't match the model
        return QuotaStatus(current_usage=0, limit=0, reset_time="Error parsing quota")