"""Utility functions for email classification."""

from email_classification.utils.logger import setup_logging
from email_classification.utils.validation import validate_email_content

__all__ = ["setup_logging", "validate_email_content"]