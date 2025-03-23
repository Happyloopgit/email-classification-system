"""Parse and extract content from email files and objects."""

import email
import os
import base64
import logging
from email.message import EmailMessage
from email.parser import BytesParser, Parser
from email import policy
from typing import Dict, Any, List, Optional, Union, BinaryIO, TextIO

from email_classification.extraction.email_content import EmailContent

logger = logging.getLogger(__name__)

class EmailParser:
    """Parse email files into structured content."""
    
    def __init__(self, attachments_dir: str = "attachments"):
        """Initialize email parser.
        
        Args:
            attachments_dir: Directory to save extracted attachments
        """
        self.attachments_dir = attachments_dir
        os.makedirs(attachments_dir, exist_ok=True)
        logger.info(f"Initialized EmailParser with attachments directory: {attachments_dir}")
    
    def _extract_attachments(self, msg: EmailMessage) -> List[Dict[str, Any]]:
        """Extract attachments from an email message.
        
        Args:
            msg: Email message object
            
        Returns:
            List of attachment dictionaries with metadata and file paths
        """
        attachments = []
        
        for part in msg.iter_attachments():
            content_type = part.get_content_type()
            content_disposition = part.get_content_disposition()
            filename = part.get_filename()
            
            if not filename:
                continue  # Skip attachments without filenames
                
            # Sanitize filename
            filename = os.path.basename(filename)
            
            # Save attachment to disk
            file_path = os.path.join(self.attachments_dir, filename)
            payload = part.get_payload(decode=True)
            
            try:
                with open(file_path, 'wb') as f:
                    f.write(payload)
                    
                # Create attachment metadata
                attachment = {
                    "filename": filename,
                    "content_type": content_type,
                    "disposition": content_disposition,
                    "size": len(payload),
                    "file_path": file_path
                }
                
                attachments.append(attachment)
                logger.debug(f"Extracted attachment: {filename}")
                
            except Exception as e:
                logger.error(f"Error saving attachment {filename}: {str(e)}")
                
        return attachments
    
    def _get_email_date(self, msg: EmailMessage) -> str:
        """Extract date from email message."""
        date_str = msg.get("Date", "")
        if not date_str:
            # Try alternative date headers
            for header in ["Delivery-Date", "Received"]:
                if header in msg:
                    date_str = msg.get(header, "")
                    break
        return date_str
    
    def _get_plain_text(self, msg: EmailMessage) -> str:
        """Extract plain text content from email message."""
        plain_text = ""
        
        # Try to get the plain text part
        for part in msg.iter_parts():
            if part.get_content_type() == "text/plain":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    plain_text = payload.decode(charset, errors='replace')
                    break
                except Exception as e:
                    logger.error(f"Error decoding plain text: {str(e)}")
        
        # If no plain text part, check if the message itself is plain text
        if not plain_text and msg.get_content_type() == "text/plain":
            try:
                charset = msg.get_content_charset() or 'utf-8'
                payload = msg.get_payload(decode=True)
                if payload:
                    plain_text = payload.decode(charset, errors='replace')
            except Exception as e:
                logger.error(f"Error decoding message plain text: {str(e)}")
        
        return plain_text
    
    def _get_html_content(self, msg: EmailMessage) -> str:
        """Extract HTML content from email message."""
        html_content = ""
        
        # Try to get the HTML part
        for part in msg.iter_parts():
            if part.get_content_type() == "text/html":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    html_content = payload.decode(charset, errors='replace')
                    break
                except Exception as e:
                    logger.error(f"Error decoding HTML content: {str(e)}")
        
        # If no HTML part, check if the message itself is HTML
        if not html_content and msg.get_content_type() == "text/html":
            try:
                charset = msg.get_content_charset() or 'utf-8'
                payload = msg.get_payload(decode=True)
                if payload:
                    html_content = payload.decode(charset, errors='replace')
            except Exception as e:
                logger.error(f"Error decoding message HTML: {str(e)}")
        
        return html_content
    
    def parse_file(self, file_path: str) -> EmailContent:
        """Parse an email file into EmailContent.
        
        Args:
            file_path: Path to the email file
            
        Returns:
            Structured EmailContent object
        """
        try:
            with open(file_path, 'rb') as fp:
                msg = BytesParser(policy=policy.default).parse(fp)
                return self._parse_message(msg)
                
        except Exception as e:
            logger.error(f"Error parsing email file {file_path}: {str(e)}")
            raise
    
    def parse_string(self, email_str: str) -> EmailContent:
        """Parse an email string into EmailContent.
        
        Args:
            email_str: Raw email content as string
            
        Returns:
            Structured EmailContent object
        """
        try:
            msg = Parser(policy=policy.default).parsestr(email_str)
            return self._parse_message(msg)
                
        except Exception as e:
            logger.error(f"Error parsing email string: {str(e)}")
            raise
    
    def _parse_message(self, msg: EmailMessage) -> EmailContent:
        """Parse an email message object into EmailContent.
        
        Args:
            msg: Email message object
            
        Returns:
            Structured EmailContent object
        """
        try:
            # Extract basic metadata
            subject = msg.get("Subject", "")
            from_address = msg.get("From", "")
            date = self._get_email_date(msg)
            
            # Extract content
            plain_text = self._get_plain_text(msg)
            html_content = self._get_html_content(msg)
            
            # Extract attachments
            attachments = self._extract_attachments(msg)
            
            # Create EmailContent object
            email_content = EmailContent(
                subject=subject,
                from_address=from_address,
                date=date,
                plain_text=plain_text,
                html_content=html_content,
                attachments=attachments
            )
            
            logger.info(f"Successfully parsed email: {subject}")
            return email_content
                
        except Exception as e:
            logger.error(f"Error parsing email message: {str(e)}")
            raise