"""FastAPI router for email classification API."""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel

from email_classification.extraction.email_content import EmailContent
from email_classification.extraction.extraction_service import ExtractionService
from email_classification.classification.classifier import EmailClassifier
from email_classification.duplicate_detection.vector_store import EmailVectorStore
from email_classification.dependencies import get_extraction_service, get_classifier, get_vector_store

router = APIRouter(prefix="/api/v1", tags=["email-classification"])


class ClassificationResponse(BaseModel):
    """Response model for classification results."""
    request_type: str
    confidence: float
    extracted_fields: Dict[str, Any]
    is_duplicate: bool = False
    similar_emails: List[Dict[str, Any]] = []


@router.post("/classify", response_model=ClassificationResponse)
async def classify_email(
    email_content: str = Form(...),
    email_subject: str = Form(...),
    email_from: str = Form(...),
    email_date: str = Form(...),
    attachment: Optional[UploadFile] = File(None),
    extraction_service: ExtractionService = Depends(get_extraction_service),
    classifier: EmailClassifier = Depends(get_classifier),
    vector_store: EmailVectorStore = Depends(get_vector_store)
):
    """
    Classify an email and extract relevant information.
    
    Args:
        email_content: The body of the email
        email_subject: The subject of the email
        email_from: The sender of the email
        email_date: The date the email was sent
        attachment: Optional attachment file
        extraction_service: Service for extracting information from emails
        classifier: Service for classifying emails
        vector_store: Service for detecting duplicate emails
    
    Returns:
        Classification results including request type, confidence,
        extracted fields, and duplicate detection information
    """
    # Create EmailContent object
    email = EmailContent(
        subject=email_subject,
        from_address=email_from,
        date=email_date,
        plain_text=email_content,
        html_content="",  # Not provided in this API endpoint
        attachments=[]  # Handle attachment processing separately if needed
    )
    
    # Process attachment if provided
    if attachment:
        file_content = await attachment.read()
        email.attachments.append({
            "filename": attachment.filename,
            "content": file_content,
            "content_type": attachment.content_type
        })
    
    # Classify email
    classification_result = classifier.classify(email)
    request_type = classification_result["request_type"]
    confidence = classification_result["confidence"]
    
    # Extract information based on classification
    extracted_fields = extraction_service.extract(email, request_type)
    
    # Check for duplicates
    similar_emails = vector_store.find_similar_emails(email, threshold=0.9)
    is_duplicate = len(similar_emails) > 0
    
    # Only add to vector store if it's not a duplicate
    if not is_duplicate:
        vector_store.add_email(email, request_type, extracted_fields)
        vector_store.save()
    
    # Format similar emails for response
    formatted_similar_emails = []
    for email_data, score in similar_emails:
        formatted_similar_emails.append({
            "subject": email_data.get("subject", ""),
            "from": email_data.get("from_address", ""),
            "date": email_data.get("date", ""),
            "request_type": email_data.get("request_type", ""),
            "similarity_score": score
        })
    
    return ClassificationResponse(
        request_type=request_type,
        confidence=confidence,
        extracted_fields=extracted_fields,
        is_duplicate=is_duplicate,
        similar_emails=formatted_similar_emails
    )


@router.get("/request-types", response_model=List[str])
async def get_request_types(
    classifier: EmailClassifier = Depends(get_classifier)
):
    """
    Get list of supported request types.
    
    Returns:
        List of request types that the system can classify
    """
    return classifier.get_supported_request_types()