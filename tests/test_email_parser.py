"""Tests for the email parser module."""

import os
import pytest
from pathlib import Path
from email.message import EmailMessage

# Adjust import paths based on your project structure
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_classification.email_parser.parser import EmailParser
from src.email_classification.extraction.email_content import EmailContent

# Test fixtures
@pytest.fixture
def email_parser():
    """Create an EmailParser instance for testing."""
    # Use a temporary directory for attachments
    attachments_dir = "test_attachments"
    os.makedirs(attachments_dir, exist_ok=True)
    parser = EmailParser(attachments_dir=attachments_dir)
    yield parser
    # Clean up
    for file in os.listdir(attachments_dir):
        os.remove(os.path.join(attachments_dir, file))
    os.rmdir(attachments_dir)

@pytest.fixture
def sample_email_string():
    """Sample email content as a string."""
    return """
From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 24 Jul 2023 10:15:30 -0400
Content-Type: text/plain; charset="utf-8"

This is a test email.
"""

# Tests
def test_parse_string(email_parser, sample_email_string):
    """Test parsing an email from a string."""
    email_content = email_parser.parse_string(sample_email_string)
    
    assert isinstance(email_content, EmailContent)
    assert email_content.subject == "Test Email"
    assert email_content.from_address == "sender@example.com"
    assert "This is a test email." in email_content.plain_text
    assert not email_content.attachments

def test_extract_date(email_parser):
    """Test date extraction from email."""
    # Create a test email message
    msg = EmailMessage()
    msg["Date"] = "Mon, 24 Jul 2023 10:15:30 -0400"
    
    date_str = email_parser._get_email_date(msg)
    assert date_str == "Mon, 24 Jul 2023 10:15:30 -0400"
    
    # Test with missing date
    msg = EmailMessage()
    date_str = email_parser._get_email_date(msg)
    assert date_str == ""

def test_get_plain_text(email_parser):
    """Test plain text extraction from email."""
    # This is a placeholder test - in a real test suite, you would
    # create proper email message objects with multipart content
    msg = EmailMessage()
    msg.set_content("This is plain text content.")
    
    plain_text = email_parser._get_plain_text(msg)
    assert "This is plain text content." in plain_text

# Additional tests would cover:
# - Parsing files
# - Extracting HTML content
# - Handling attachments
# - Error cases