"""Validation utilities for email content."""

from typing import Dict, Any, List, Optional
import logging
import re

from email_classification.extraction.email_content import EmailContent

logger = logging.getLogger(__name__)

def validate_email_content(email: EmailContent) -> Dict[str, Any]:
    """Validate email content and report any issues.
    
    Args:
        email: EmailContent object to validate
        
    Returns:
        Dictionary with validation results
    """
    issues = []
    
    # Check required fields
    if not email.subject:
        issues.append("Missing subject")
    
    if not email.from_address:
        issues.append("Missing sender address")
    
    # Validate email address format
    if email.from_address and not _is_valid_email(email.from_address):
        issues.append(f"Invalid sender email format: {email.from_address}")
    
    # Check content
    if not email.plain_text and not email.html_content:
        issues.append("Email has no content (neither plain text nor HTML)")
    
    # Validate attachments if present
    if email.attachments:
        for i, attachment in enumerate(email.attachments):
            if "filename" not in attachment:
                issues.append(f"Attachment {i+1} is missing filename")
            if "content_type" not in attachment:
                issues.append(f"Attachment {i+1} is missing content type")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues
    }

def _is_valid_email(email_address: str) -> bool:
    """Check if the email address has a valid format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email_address))

def sanitize_input(text: str) -> str:
    """Sanitize input text to prevent security issues.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove potentially dangerous HTML tags
    text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text, flags=re.IGNORECASE)
    
    # Remove other potentially malicious tags
    text = re.sub(r'<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>', '', text, flags=re.IGNORECASE)
    
    # Strip excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text