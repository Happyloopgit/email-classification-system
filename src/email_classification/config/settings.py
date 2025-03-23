"""Configuration settings for the email classification system."""

from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_TITLE: str = "Email Classification System"
    API_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    
    # LLM Configuration
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4"
    
    # Classification Configuration
    CONFIDENCE_THRESHOLD: float = 0.7
    REQUEST_TYPES: List[str] = [
        "Adjustment",
        "AU Transfer",
        "Closing Notice",
        "Commitment Change",
        "Fee Payment",
        "Money Movement Inbound",
        "Money Movement Outbound"
    ]
    
    # Extraction Configuration
    COMMON_FIELDS: List[str] = [
        "deal_name", 
        "amount", 
        "expiration_date", 
        "effective_date"
    ]
    
    # Type-specific extraction fields
    REQUEST_TYPE_FIELDS: Dict[str, List[str]] = {
        "Adjustment": ["adjustment_type", "adjustment_reason"],
        "AU Transfer": ["source_account", "destination_account", "transfer_date"],
        "Closing Notice": ["closing_date", "borrower_name", "facility_type"],
        "Commitment Change": ["change_type", "old_amount", "new_amount"],
        "Fee Payment": ["fee_type", "payment_method", "due_date"],
        "Money Movement Inbound": ["sender_account", "received_amount", "reference_number"],
        "Money Movement Outbound": ["recipient_account", "send_amount", "reference_number"]
    }
    
    # Duplicate Detection Configuration
    SIMILARITY_THRESHOLD: float = 0.85
    
    # Vector Store Configuration
    VECTOR_STORE_PATH: str = "./vector_store"
    
    # Document Processing Configuration
    MAX_DOCUMENT_SIZE_MB: int = 10
    SUPPORTED_EXTENSIONS: List[str] = ["pdf", "docx", "doc", "eml", "txt"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()