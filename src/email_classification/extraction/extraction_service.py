"""Service for extracting information from emails."""

from typing import Dict, Any
import logging

from email_classification.extraction.email_content import EmailContent
from email_classification.extraction.processors import (
    TextProcessor,
    DocumentProcessor,
    EntityProcessor
)

logger = logging.getLogger(__name__)

class ExtractionService:
    """Service for extracting information from emails."""
    
    def __init__(
        self,
        text_processor: TextProcessor,
        document_processor: DocumentProcessor,
        entity_processor: EntityProcessor
    ):
        """Initialize extraction service."""
        self.text_processor = text_processor
        self.document_processor = document_processor
        self.entity_processor = entity_processor
    
    def extract(self, email: EmailContent, request_type: str) -> Dict[str, Any]:
        """Extract information from email based on request type."""
        try:
            # Process text content
            text_results = self.text_processor.process_text(email.plain_text)
            
            # Process attachments if any
            attachment_results = []
            for attachment in email.attachments:
                result = self.document_processor.process_document(attachment)
                attachment_results.append(result)
            
            # Extract entities
            entity_results = self.entity_processor.extract_entities(email.plain_text)
            
            # Placeholder implementation - in a real system, this would be
            # more sophisticated and would use the request type to determine
            # what to extract
            return {
                "request_type": request_type,
                "subject": email.subject,
                "sender": email.from_address,
                "date": email.date,
                "entities": entity_results.get("entities", []),
                "attachments_processed": len(attachment_results),
                # Add dummy fields for now
                "amount": "$1000.00",
                "reference_number": "REF123456",
                "account_number": "ACCT-98765"
            }
        except Exception as e:
            logger.error(f"Error extracting information: {str(e)}")
            return {"error": str(e)}