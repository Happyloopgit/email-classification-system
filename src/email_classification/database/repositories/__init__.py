"""Repository pattern implementations for database access."""

from email_classification.database.repositories.email_repository import EmailRepository
from email_classification.database.repositories.classification_repository import ClassificationRepository
from email_classification.database.repositories.extraction_repository import ExtractionRepository
from email_classification.database.repositories.report_repository import ReportRepository

__all__ = [
    "EmailRepository",
    "ClassificationRepository",
    "ExtractionRepository",
    "ReportRepository"
]