import os.path
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from models.email_models import EmailMessage

# If modifying these scopes, delete token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailClient:
    """A client to interact with the Gmail API."""

    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
        Initializes the GmailClient, handling authentication.
        
        Args:
            credentials_path: Path to the OAuth 2.0 client secrets file.
            token_path: Path to store the user's token.
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = self._get_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def _get_credentials(self) -> Credentials:
        """
        Gets user credentials for the Gmail API.
        Handles loading from file, refreshing expired tokens, or
        initiating a new OAuth 2.0 authorization flow.
        """
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or creds.token_state.name != "FRESH":
            if creds and creds.token_state.name != "FRESH" and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at '{self.credentials_path}'. "
                        "Please download it from the Google Cloud Console and place it in the project root."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                assert isinstance(creds, Credentials)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        return creds

    def create_message(self, email_data: EmailMessage) -> dict:
        """
        Creates a raw email message dictionary for the Gmail API.

        Args:
            email_data: An EmailMessage object with email details.

        Returns:
            A dictionary with a 'raw' key containing the base64url-encoded message.
        """
        message = MIMEText(email_data.body, email_data.format)
        message['to'] = email_data.to
        message['subject'] = email_data.subject
        if email_data.cc:
            message['cc'] = ', '.join(email_data.cc)
        if email_data.bcc:
            message['bcc'] = ', '.join(email_data.bcc)
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': encoded_message}

    def send_email(self, email_data: EmailMessage) -> dict:
        """
        Sends a single email using the authenticated client.

        Args:
            email_data: An EmailMessage object.

        Returns:
            The response from the Gmail API upon success, or an error dictionary.
        """
        try:
            created_message = self.create_message(email_data)
            sent_message = self.service.users().messages().send(
                userId='me',
                body=created_message
            ).execute()
            return sent_message
        except HttpError as error:
            return {'error': str(error)}

    def get_quota_status(self) -> dict:
        """
        Provides a placeholder for Gmail API quota status.
        Note: The standard Gmail API does not offer a direct method to check daily
        quota usage. This information is available in the Google Cloud Console.
        """
        # This is a mock response as per the note above.
        return {
            "current_usage": "Unknown",
            "limit": "500 emails/day (for a standard @gmail.com account)",
            "reset_time": "Resets every 24 hours"
        }