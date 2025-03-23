#!/usr/bin/env python
"""
Example script for processing a single email file.

Usage:
    python process_email.py path/to/email.eml
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_classification.utils import setup_logging
from src.email_classification.email_parser import EmailParser
from src.email_classification.classification.classifier import EmailClassifier
from src.email_classification.duplicate_detection.vector_store import EmailVectorStore
from src.email_classification.classification.classification_service import ClassificationService
from src.email_classification.extraction.processors import TextProcessor, DocumentProcessor, EntityProcessor
from src.email_classification.extraction.extraction_service import ExtractionService
from src.email_classification.reporting.report_generator import ReportGenerator
from src.email_classification.reporting.export_service import ExportService

def main():
    # Set up logging
    setup_logging(log_level="INFO")
    logger = logging.getLogger(__name__)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} path/to/email.eml")
        sys.exit(1)
    
    email_path = sys.argv[1]
    if not os.path.exists(email_path):
        print(f"Error: File {email_path} does not exist.")
        sys.exit(1)
    
    # Create output directories
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("exports", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    try:
        # Initialize components
        parser = EmailParser(attachments_dir="attachments")
        classifier = EmailClassifier(threshold=0.6)
        vector_store = EmailVectorStore(vector_dim=384, model_name="all-MiniLM-L6-v2")
        classification_service = ClassificationService(
            classifier=classifier,
            vector_store=vector_store,
            duplicate_threshold=0.95
        )
        
        text_processor = TextProcessor()
        document_processor = DocumentProcessor(ocr_enabled=True)
        entity_processor = EntityProcessor()
        extraction_service = ExtractionService(
            text_processor=text_processor,
            document_processor=document_processor,
            entity_processor=entity_processor
        )
        
        report_generator = ReportGenerator(output_dir="reports")
        export_service = ExportService(report_generator=report_generator, export_dir="exports")
        
        # Parse email
        logger.info(f"Processing email: {email_path}")
        email_content = parser.parse_file(email_path)
        
        # Classify email and check for duplicates
        classification_result = classification_service.process_email(email_content)
        request_type = classification_result["request_type"]
        is_duplicate = classification_result["is_duplicate"]
        
        logger.info(f"Email classified as {request_type} (duplicate: {is_duplicate})")
        
        # Extract information if not a duplicate
        if not is_duplicate:
            extracted_data = extraction_service.extract(email_content, request_type)
            
            # Generate reports
            pdf_path = export_service.generate_report(extracted_data, format_type="pdf")
            json_path = export_service.generate_report(extracted_data, format_type="json")
            
            logger.info(f"Generated PDF report: {pdf_path}")
            logger.info(f"Generated JSON report: {json_path}")
            
            # Print extracted information
            print("\nExtracted Information:")
            print(json.dumps(extracted_data, indent=2))
        else:
            similar_emails = classification_result.get("similar_emails", [])
            print("\nDuplicate email detected!")
            print(f"Found {len(similar_emails)} similar emails.")
            for i, (similarity, metadata) in enumerate(similar_emails[:3], 1):
                print(f"Similar email #{i}: {metadata.get('subject', 'Unknown')} ")
                print(f"Similarity: {similarity:.4f}")
        
        print("\nProcessing complete!")
        
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()