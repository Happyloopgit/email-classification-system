"""Tests for the email classifier module."""

import pytest
from pathlib import Path

# Adjust import paths based on your project structure
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_classification.classification.classifier import EmailClassifier
from src.email_classification.extraction.email_content import EmailContent

# Test fixtures
@pytest.fixture
def email_classifier():
    """Create an EmailClassifier instance for testing."""
    return EmailClassifier(threshold=0.6)

@pytest.fixture
def sample_emails():
    """Sample emails for testing classification."""
    return {
        "reimbursement": EmailContent(
            subject="Expense Reimbursement Request",
            from_address="employee@example.com",
            date="2023-07-24",
            plain_text="I need to be reimbursed for travel expenses totaling $450.20.",
            html_content="<p>I need to be reimbursed for travel expenses totaling $450.20.</p>"
        ),
        "invoice": EmailContent(
            subject="Invoice #12345 Payment",
            from_address="vendor@example.com",
            date="2023-07-24",
            plain_text="Please process payment for invoice #12345 for $1,250.00.",
            html_content="<p>Please process payment for invoice #12345 for $1,250.00.</p>"
        ),
        "account": EmailContent(
            subject="Account Balance Inquiry",
            from_address="customer@example.com",
            date="2023-07-24",
            plain_text="I would like to know my current account balance.",
            html_content="<p>I would like to know my current account balance.</p>"
        ),
        "statement": EmailContent(
            subject="Monthly Statement Request",
            from_address="customer@example.com",
            date="2023-07-24",
            plain_text="Please send me my monthly account statement.",
            html_content="<p>Please send me my monthly account statement.</p>"
        ),
        "other": EmailContent(
            subject="General Question",
            from_address="person@example.com",
            date="2023-07-24",
            plain_text="I have a question about your services.",
            html_content="<p>I have a question about your services.</p>"
        )
    }

# Tests
def test_classifier_initialization(email_classifier):
    """Test that the classifier initializes correctly."""
    assert email_classifier.threshold == 0.6
    assert isinstance(email_classifier.request_types, list)
    assert len(email_classifier.request_types) > 0

def test_feature_preparation(email_classifier, sample_emails):
    """Test feature preparation for classification."""
    email = sample_emails["reimbursement"]
    features = email_classifier._prepare_features(email)
    
    assert "subject" in features
    assert "body" in features
    assert "has_attachments" in features
    assert features["subject"] == "Expense Reimbursement Request"

def test_classification(email_classifier, sample_emails):
    """Test email classification."""
    # Test reimbursement email
    request_type, confidence = email_classifier.classify(sample_emails["reimbursement"])
    assert request_type == "REIMBURSEMENT"
    assert confidence > 0.7
    
    # Test invoice email
    request_type, confidence = email_classifier.classify(sample_emails["invoice"])
    assert request_type == "INVOICE_PAYMENT"
    assert confidence > 0.7
    
    # Test account email
    request_type, confidence = email_classifier.classify(sample_emails["account"])
    assert request_type == "ACCOUNT_INQUIRY"
    assert confidence > 0.7
    
    # Test statement email
    request_type, confidence = email_classifier.classify(sample_emails["statement"])
    assert request_type == "STATEMENT_REQUEST"
    assert confidence > 0.7
    
    # Test other email
    request_type, confidence = email_classifier.classify(sample_emails["other"])
    assert request_type == "OTHER"
    assert confidence > 0.0

def test_get_all_request_types(email_classifier):
    """Test retrieving all request types."""
    request_types = email_classifier.get_all_request_types()
    assert isinstance(request_types, list)
    assert len(request_types) > 0
    assert "REIMBURSEMENT" in request_types
    assert "INVOICE_PAYMENT" in request_types

# Additional tests would cover:
# - Edge cases
# - Error handling
# - Different thresholds