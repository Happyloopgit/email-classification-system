"""Module for email content representation."""

from typing import List, Dict, Any, Optional

class EmailContent:
    """Represents an email content object."""
    
    def __init__(
        self,
        subject: str,
        from_address: str,
        date: str,
        plain_text: str,
        html_content: str = "",
        attachments: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize email content.
        
        Args:
            subject: Email subject
            from_address: Sender's email address
            date: Email date string
            plain_text: Plain text content of the email
            html_content: HTML content of the email (if any)
            attachments: List of attachment objects
        """
        self.subject = subject
        self.from_address = from_address
        self.date = date
        self.plain_text = plain_text
        self.html_content = html_content
        self.attachments = attachments or []
    
    def __str__(self) -> str:
        return f"{self.subject} from {self.from_address}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert email content to dictionary."""
        return {
            "subject": self.subject,
            "from_address": self.from_address,
            "date": self.date,
            "plain_text": self.plain_text,
            "html_content": self.html_content,
            "attachments": self.attachments
        }