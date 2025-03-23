"""Dependency injection for FastAPI."""
import os
from functools import lru_cache
from typing import Dict, Any

from email_classification.extraction.extraction_service import ExtractionService
from email_classification.extraction.processors import (
    TextProcessor,
    DocumentProcessor,
    EntityProcessor
)
from email_classification.classification.classifier import EmailClassifier
from email_classification.duplicate_detection.vector_store import EmailVectorStore

# Configuration (could be loaded from environment variables or config file)
CONFIG: Dict[str, Any] = {
    "classifier": {
        "model_name": os.getenv("CLASSIFIER_MODEL", "all-MiniLM-L6-v2"),
        "request_types": [
            "information_request",
            "change_request",
            "complaint",
            "feedback",
            "account_update",
            "technical_support",
            "billing_inquiry"
        ]
    },
    "vector_store": {
        "model_name": os.getenv("VECTOR_STORE_MODEL", "all-MiniLM-L6-v2"),
        "threshold": float(os.getenv("SIMILARITY_THRESHOLD", "0.9"))
    },
    "extraction": {
        "llm_model": os.getenv("EXTRACTION_LLM_MODEL", "gpt-4"),
        "ocr_enabled": os.getenv("OCR_ENABLED", "true").lower() == "true",
        "language": os.getenv("LANGUAGE", "en")
    }
}


@lru_cache()
def get_text_processor() -> TextProcessor:
    """Get text processor instance."""
    return TextProcessor()


@lru_cache()
def get_document_processor() -> DocumentProcessor:
    """Get document processor instance."""
    return DocumentProcessor(ocr_enabled=CONFIG["extraction"]["ocr_enabled"])


@lru_cache()
def get_entity_processor() -> EntityProcessor:
    """Get entity processor instance."""
    return EntityProcessor(
        language=CONFIG["extraction"]["language"],
        llm_model=CONFIG["extraction"]["llm_model"]
    )


@lru_cache()
def get_extraction_service() -> ExtractionService:
    """Get extraction service instance."""
    return ExtractionService(
        text_processor=get_text_processor(),
        document_processor=get_document_processor(),
        entity_processor=get_entity_processor()
    )


@lru_cache()
def get_classifier() -> EmailClassifier:
    """Get email classifier instance."""
    return EmailClassifier(
        model_name=CONFIG["classifier"]["model_name"],
        request_types=CONFIG["classifier"]["request_types"]
    )


@lru_cache()
def get_vector_store() -> EmailVectorStore:
    """Get vector store instance."""
    return EmailVectorStore(
        model_name=CONFIG["vector_store"]["model_name"]
    )