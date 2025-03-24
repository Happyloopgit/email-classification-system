"""Email service for integrating with email providers."""

from email_classification.email_service.imap_client import ImapClient
from email_classification.email_service.smtp_client import SmtpClient
from email_classification.email_service.email_fetcher import EmailFetcher

__all__ = ["ImapClient", "SmtpClient", "EmailFetcher"]