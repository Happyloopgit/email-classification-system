#!/usr/bin/env python
"""
Example client script for the Email Classification API.

This script demonstrates how to make requests to the API endpoints 
and handle the responses.
"""
import argparse
import json
import os
import requests
from typing import Dict, Any, Optional


class EmailClassificationClient:
    """Client for interacting with the Email Classification API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client with the API base URL.
        
        Args:
            base_url: Base URL of the API, defaults to http://localhost:8000
        """
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def get_request_types(self) -> list:
        """
        Get list of supported request types.
        
        Returns:
            List of request types
        """
        response = requests.get(f"{self.api_url}/request-types")
        response.raise_for_status()
        return response.json()
    
    def classify_email(
        self,
        email_content: str,
        email_subject: str,
        email_from: str,
        email_date: str,
        attachment_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify an email and extract information.
        
        Args:
            email_content: The body of the email
            email_subject: The subject of the email
            email_from: The sender of the email
            email_date: The date the email was sent
            attachment_path: Optional path to an attachment file
            
        Returns:
            Classification results including request type, confidence,
            extracted fields, and duplicate detection information
        """
        url = f"{self.api_url}/classify"
        data = {
            "email_content": email_content,
            "email_subject": email_subject,
            "email_from": email_from,
            "email_date": email_date
        }
        
        files = {}
        if attachment_path and os.path.exists(attachment_path):
            file_name = os.path.basename(attachment_path)
            content_type = self._get_content_type(file_name)
            files = {
                "attachment": (file_name, open(attachment_path, "rb"), content_type)
            }
        
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        
        # Close files if they were opened
        if files and "attachment" in files:
            files["attachment"][1].close()
            
        return response.json()
    
    def _get_content_type(self, file_name: str) -> str:
        """
        Get content type based on file extension.
        
        Args:
            file_name: Name of the file
            
        Returns:
            MIME content type
        """
        extension = os.path.splitext(file_name)[1].lower()
        content_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".txt": "text/plain"
        }
        return content_types.get(extension, "application/octet-stream")


def main():
    """Main function to run the client script."""
    parser = argparse.ArgumentParser(description="Email Classification API Client")
    parser.add_argument("--server", default="http://localhost:8000", help="API server URL")
    parser.add_argument("--subject", default="Sample Invoice #12345", help="Email subject")
    parser.add_argument("--from", dest="from_addr", default="billing@example.com", help="Email from address")
    parser.add_argument("--date", default="2023-09-15T14:30:00Z", help="Email date")
    parser.add_argument("--attachment", help="Path to attachment file")
    parser.add_argument("--content", help="Email content text")
    parser.add_argument("--content-file", help="File containing email content")
    
    args = parser.parse_args()
    
    # Get email content from file or command line argument
    email_content = args.content
    if args.content_file and not email_content:
        with open(args.content_file, "r", encoding="utf-8") as f:
            email_content = f.read()
    
    if not email_content:
        email_content = """
        Hello,
        
        Please find attached the invoice for your recent order #12345.
        The total amount due is $1,250.00, payable by November 15, 2023.
        
        If you have any questions about this invoice, please let me know.
        
        Best regards,
        Billing Department
        """
    
    # Create client and make API calls
    client = EmailClassificationClient(args.server)
    
    print("Supported request types:")
    request_types = client.get_request_types()
    print(json.dumps(request_types, indent=2))
    print()
    
    print("Classifying email:")
    result = client.classify_email(
        email_content=email_content,
        email_subject=args.subject,
        email_from=args.from_addr,
        email_date=args.date,
        attachment_path=args.attachment
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()