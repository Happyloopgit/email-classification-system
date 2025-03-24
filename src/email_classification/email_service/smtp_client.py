"""SMTP client for sending emails."""

import smtplib
import logging
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class SmtpClient:
    """SMTP client for sending emails."""
    
    def __init__(
        self,
        server: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True
    ):
        """Initialize the SMTP client.
        
        Args:
            server: SMTP server address
            port: SMTP server port
            username: Email account username
            password: Email account password
            use_tls: Whether to use TLS for connection
        """
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.connection = None
        
        logger.info(f"Initialized SMTP client for {username} on {server}:{port}")
    
    def connect(self) -> bool:
        """Connect to the SMTP server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create connection
            self.connection = smtplib.SMTP(self.server, self.port)
            
            # Use TLS if specified
            if self.use_tls:
                self.connection.starttls()
            
            # Login to the server
            self.connection.login(self.username, self.password)
            logger.info(f"Connected to SMTP server: {self.server}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the SMTP server."""
        try:
            if self.connection:
                self.connection.quit()
                self.connection = None
                logger.info("Disconnected from SMTP server")
        except Exception as e:
            logger.error(f"Error disconnecting from SMTP server: {str(e)}")
    
    def send_email(
        self, 
        to_address: Union[str, List[str]], 
        subject: str, 
        body_text: str, 
        body_html: Optional[str] = None,
        cc_address: Optional[Union[str, List[str]]] = None,
        bcc_address: Optional[Union[str, List[str]]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """Send an email.
        
        Args:
            to_address: Recipient email address(es)
            subject: Email subject
            body_text: Plain text email body
            body_html: Optional HTML email body
            cc_address: Optional CC recipient(s)
            bcc_address: Optional BCC recipient(s)
            attachments: Optional list of attachment dictionaries
                         Each attachment should have 'file_path' and optionally 'filename'
            reply_to: Optional reply-to address
            
        Returns:
            True if sending was successful, False otherwise
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            
            # Handle recipients
            if isinstance(to_address, list):
                msg['To'] = ', '.join(to_address)
            else:
                msg['To'] = to_address
            
            # Add CC if provided
            if cc_address:
                if isinstance(cc_address, list):
                    msg['Cc'] = ', '.join(cc_address)
                else:
                    msg['Cc'] = cc_address
            
            # Add Reply-To if provided
            if reply_to:
                msg['Reply-To'] = reply_to
            
            # Add text part
            msg.attach(MIMEText(body_text, 'plain'))
            
            # Add HTML part if provided
            if body_html:
                msg.attach(MIMEText(body_html, 'html'))
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    file_path = attachment['file_path']
                    filename = attachment.get('filename', Path(file_path).name)
                    
                    with open(file_path, 'rb') as f:
                        part = MIMEApplication(f.read(), Name=filename)
                    
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    msg.attach(part)
            
            # Prepare recipient list
            recipients = [to_address] if isinstance(to_address, str) else to_address
            
            if cc_address:
                if isinstance(cc_address, str):
                    recipients.append(cc_address)
                else:
                    recipients.extend(cc_address)
            
            if bcc_address:
                if isinstance(bcc_address, str):
                    recipients.append(bcc_address)
                else:
                    recipients.extend(bcc_address)
            
            # Send the email
            self.connection.send_message(msg)
            
            logger.info(f"Sent email with subject '{subject}' to {to_address}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_report_email(
        self,
        to_address: Union[str, List[str]],
        subject: str,
        report_data: Dict[str, Any],
        report_files: Optional[List[str]] = None
    ) -> bool:
        """Send an email with processing results.
        
        Args:
            to_address: Recipient email address(es)
            subject: Email subject
            report_data: Dictionary of report data
            report_files: Optional list of report file paths to attach
            
        Returns:
            True if sending was successful, False otherwise
        """
        try:
            # Prepare text body
            body_text = f"Email Classification Report\n\n"
            body_text += f"Request Type: {report_data.get('request_type', 'Unknown')}\n"
            body_text += f"Confidence: {report_data.get('confidence', 0.0):.2f}\n\n"
            
            # Add extraction results
            body_text += "Extracted Information:\n"
            for key, value in report_data.items():
                if key not in ['request_type', 'confidence', 'entities'] and not isinstance(value, (dict, list)):
                    body_text += f"{key}: {value}\n"
            
            # Prepare HTML body
            body_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: #f0f0f0; padding: 10px; }}
                    .content {{ padding: 15px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>Email Classification Report</h2>
                    <p><strong>Request Type:</strong> {report_data.get('request_type', 'Unknown')}</p>
                    <p><strong>Confidence:</strong> {report_data.get('confidence', 0.0):.2f}</p>
                </div>
                <div class="content">
                    <h3>Extracted Information</h3>
                    <table>
                        <tr>
                            <th>Field</th>
                            <th>Value</th>
                        </tr>
            """
            
            # Add table rows for each field
            for key, value in report_data.items():
                if key not in ['request_type', 'confidence', 'entities'] and not isinstance(value, (dict, list)):
                    body_html += f"""
                        <tr>
                            <td>{key}</td>
                            <td>{value}</td>
                        </tr>
                    """
            
            body_html += """
                    </table>
                </div>
            </body>
            </html>
            """
            
            # Prepare attachments
            attachments = None
            if report_files:
                attachments = [{'file_path': file_path} for file_path in report_files]
            
            # Send the email
            return self.send_email(
                to_address=to_address,
                subject=subject,
                body_text=body_text,
                body_html=body_html,
                attachments=attachments
            )
            
        except Exception as e:
            logger.error(f"Error sending report email: {str(e)}")
            return False
    
    def __enter__(self):
        """Context manager support - connect on enter."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support - disconnect on exit."""
        self.disconnect()