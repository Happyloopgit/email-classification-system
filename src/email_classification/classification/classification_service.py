"""Service for classifying emails into request types."""

from typing import Dict, Any, Tuple
import logging

from email_classification.extraction.email_content import EmailContent
from email_classification.classification.classifier import EmailClassifier
from email_classification.duplicate_detection.vector_store import EmailVectorStore

logger = logging.getLogger(__name__)

class ClassificationService:
    """Service for classifying emails and detecting duplicates."""
    
    def __init__(
        self,
        classifier: EmailClassifier,
        vector_store: EmailVectorStore,
        duplicate_threshold: float = 0.95
    ):
        """Initialize classification service.
        
        Args:
            classifier: Email classifier
            vector_store: Vector store for duplicate detection
            duplicate_threshold: Threshold for considering emails as duplicates
        """
        self.classifier = classifier
        self.vector_store = vector_store
        self.duplicate_threshold = duplicate_threshold
        logger.info("Initialized ClassificationService")
    
    def process_email(self, email: EmailContent) -> Dict[str, Any]:
        """Process an email by classifying it and checking for duplicates.
        
        Args:
            email: EmailContent object to process
            
        Returns:
            Dictionary with classification results and duplicate status
        """
        try:
            # Check for duplicates
            similar_emails = self.vector_store.find_similar_emails(
                email, top_k=5, threshold=self.duplicate_threshold
            )
            
            is_duplicate = len(similar_emails) > 0
            
            # Only classify if not a duplicate
            if not is_duplicate:
                request_type, confidence = self.classifier.classify(email)
                
                # Add email to vector store
                self.vector_store.add_email(
                    email, request_type=request_type, metadata={"confidence": confidence}
                )
                self.vector_store.save()  # Save vector store after adding new email
            else:
                # Use the request type from the most similar email
                request_type = similar_emails[0][1].get("request_type", "UNKNOWN")
                confidence = similar_emails[0][0]  # Use similarity as confidence
            
            return {
                "request_type": request_type,
                "confidence": confidence,
                "is_duplicate": is_duplicate,
                "similar_emails": [
                    {"similarity": sim, "metadata": meta}
                    for sim, meta in similar_emails
                ] if is_duplicate else []
            }
            
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            return {
                "error": str(e),
                "request_type": "ERROR",
                "confidence": 0.0,
                "is_duplicate": False,
                "similar_emails": []
            }