"""Database access module for email classification system."""

from email_classification.database.supabase_client import SupabaseClient
from email_classification.database.repositories import (
    EmailRepository,
    ClassificationRepository,
    ExtractionRepository,
    ReportRepository
)

__all__ = [
    "SupabaseClient",
    "EmailRepository",
    "ClassificationRepository",
    "ExtractionRepository",
    "ReportRepository"
]