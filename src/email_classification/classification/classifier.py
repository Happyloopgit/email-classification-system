"""Email classifier implementation."""

from typing import Dict, Any, List, Tuple
import logging

from email_classification.extraction.email_content import EmailContent

logger = logging.getLogger(__name__)

class EmailClassifier:
    """Classifies emails into request types."""
    
    def __init__(self, model_path: str = None, threshold: float = 0.7):
        """Initialize classifier.
        
        Args:
            model_path: Path to pre-trained classification model
            threshold: Confidence threshold for classification
        """
        self.model_path = model_path
        self.threshold = threshold
        self.request_types = [
            "REIMBURSEMENT", 
            "INVOICE_PAYMENT", 
            "ACCOUNT_INQUIRY",
            "STATEMENT_REQUEST",
            "OTHER"
        ]
        # In a real implementation, we would load an actual ML model here
        logger.info(f"Initialized EmailClassifier with threshold {threshold}")
        
    def _prepare_features(self, email: EmailContent) -> Dict[str, Any]:
        """Prepare features for classification."""
        # Simple feature extraction - in a real system this would be more sophisticated
        return {
            "subject": email.subject,
            "body": email.plain_text[:1000],  # Use first 1000 chars only
            "has_attachments": len(email.attachments) > 0
        }
    
    def classify(self, email: EmailContent) -> Tuple[str, float]:
        """Classify email into a request type.
        
        Args:
            email: EmailContent object to classify
            
        Returns:
            Tuple of (request_type, confidence)
        """
        try:
            # Extract features
            features = self._prepare_features(email)
            
            # This is a placeholder classification logic
            # In a real system, this would use a trained ML model
            
            # Simple rule-based classification for demonstration
            subject_lower = email.subject.lower()
            body_lower = email.plain_text.lower()
            
            # Check for request types in subject and body
            if "reimburs" in subject_lower or "reimburs" in body_lower:
                return "REIMBURSEMENT", 0.85
            elif "invoice" in subject_lower or "payment" in subject_lower:
                return "INVOICE_PAYMENT", 0.78
            elif "account" in subject_lower or "balance" in body_lower:
                return "ACCOUNT_INQUIRY", 0.72
            elif "statement" in subject_lower or "statement" in body_lower:
                return "STATEMENT_REQUEST", 0.81
            else:
                return "OTHER", 0.60
                
        except Exception as e:
            logger.error(f"Error classifying email: {str(e)}")
            return "ERROR", 0.0

    def get_all_request_types(self) -> List[str]:
        """Return all possible request types."""
        return self.request_types