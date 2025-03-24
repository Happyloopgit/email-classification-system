"""Email fetcher service for polling email accounts."""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
import threading

from email_classification.database.supabase_client import SupabaseClient
from email_classification.email_service.imap_client import ImapClient
from email_classification.email_service.smtp_client import SmtpClient
from email_classification.email_parser.parser import EmailParser
from email_classification.extraction.email_content import EmailContent

logger = logging.getLogger(__name__)

class EmailFetcher:
    """Service for fetching and processing emails from configured accounts."""
    
    def __init__(
        self,
        parser: EmailParser,
        supabase_client: Optional[SupabaseClient] = None,
        polling_interval: int = 300  # 5 minutes
    ):
        """Initialize the email fetcher.
        
        Args:
            parser: EmailParser instance for parsing emails
            supabase_client: SupabaseClient instance. If None, creates a new one.
            polling_interval: Time in seconds between polling cycles
        """
        self.parser = parser
        self.supabase = supabase_client or SupabaseClient()
        self.client = self.supabase.get_client()
        self.polling_interval = polling_interval
        self.running = False
        self.thread = None
        self.email_processors = []
        
        logger.info(f"Initialized EmailFetcher with polling interval: {polling_interval} seconds")
    
    def register_processor(self, processor: Callable[[EmailContent], Dict[str, Any]]) -> None:
        """Register an email processor function.
        
        Args:
            processor: Function that takes EmailContent and returns processing results
        """
        self.email_processors.append(processor)
        logger.info(f"Registered email processor: {processor.__name__}")
    
    def get_email_accounts(self) -> List[Dict[str, Any]]:
        """Get configured email accounts from the database.
        
        Returns:
            List of email account configurations
        """
        try:
            result = self.client.table("email_accounts").select("*").execute()
            
            if 'data' in result and result['data']:
                return result['data']
            else:
                logger.warning("No email accounts configured in the database")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving email accounts: {str(e)}")
            return []
    
    def get_account_folders(self, account_id: int) -> List[Dict[str, Any]]:
        """Get configured folders for an email account.
        
        Args:
            account_id: Email account ID
            
        Returns:
            List of folder configurations
        """
        try:
            result = self.client.table("email_folders") \
                .select("*") \
                .eq("account_id", account_id) \
                .eq("is_active", True) \
                .execute()
            
            if 'data' in result and result['data']:
                return result['data']
            else:
                logger.warning(f"No active folders configured for account ID {account_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving folders for account ID {account_id}: {str(e)}")
            return []
    
    def update_last_checked(self, folder_id: int) -> None:
        """Update the last_checked timestamp for a folder.
        
        Args:
            folder_id: Folder ID
        """
        try:
            self.client.table("email_folders").update({
                "last_checked": datetime.now().isoformat()
            }).eq("id", folder_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating last_checked for folder ID {folder_id}: {str(e)}")
    
    def log_processing(self, account_id: int, email_id: Optional[int], message_id: str, status: str, error_message: Optional[str] = None, processing_time: Optional[float] = None) -> None:
        """Log email processing results.
        
        Args:
            account_id: Email account ID
            email_id: Email record ID (if created)
            message_id: Email message ID
            status: Processing status
            error_message: Optional error message
            processing_time: Optional processing time in seconds
        """
        try:
            log_data = {
                "email_id": email_id,
                "account_id": account_id,
                "message_id": message_id,
                "status": status,
                "error_message": error_message,
                "processing_time": processing_time
            }
            
            self.client.table("email_processing_log").insert(log_data).execute()
            
        except Exception as e:
            logger.error(f"Error logging email processing: {str(e)}")
    
    def process_emails(self, account: Dict[str, Any], folder: Dict[str, Any]) -> None:
        """Process emails from a specific account and folder.
        
        Args:
            account: Email account configuration
            folder: Folder configuration
        """
        folder_name = folder.get("folder_name")
        last_checked = folder.get("last_checked")
        since_date = None
        
        if last_checked:
            try:
                # Parse ISO format date
                if isinstance(last_checked, str):
                    since_date = datetime.fromisoformat(last_checked.replace("Z", "+00:00"))
                else:
                    since_date = last_checked
                    
                # Subtract 1 hour to account for possible delays or timezone issues
                since_date -= timedelta(hours=1)
                
            except Exception as e:
                logger.error(f"Error parsing last_checked date: {str(e)}")
        
        # Connect to the IMAP server
        with ImapClient(
            server=account.get("server"),
            port=account.get("port"),
            username=account.get("username"),
            password=account.get("password"),
            use_ssl=account.get("use_ssl", True)
        ) as imap_client:
            # Select the folder
            message_count = imap_client.select_folder(folder_name)
            
            if message_count <= 0:
                logger.info(f"No messages in folder {folder_name} for account {account.get('name')}")
                return
            
            # Search for new messages
            search_criteria = "ALL"
            message_ids = imap_client.search_messages(search_criteria, since_date)
            
            logger.info(f"Found {len(message_ids)} new messages in folder {folder_name} for account {account.get('name')}")
            
            # Process each message
            for message_id in message_ids:
                # Fetch the message
                message = imap_client.fetch_message(message_id)
                
                if not message:
                    continue
                
                # Get the message ID header for tracking
                message_id_header = message.get('Message-ID', f"<{message_id}@unknown>")
                
                try:
                    start_time = time.time()
                    
                    # Parse the message
                    email_content = self.parser._parse_message(message)
                    
                    # Process the email with registered processors
                    results = {}
                    email_id = None
                    
                    for processor in self.email_processors:
                        processor_result = processor(email_content)
                        results.update(processor_result)
                        
                        # Check if the processor added an email_id
                        if 'email_id' in processor_result and processor_result['email_id']:
                            email_id = processor_result['email_id']
                    
                    # Calculate processing time
                    processing_time = time.time() - start_time
                    
                    # Mark the message as read
                    imap_client.mark_as_read(message_id)
                    
                    # Log successful processing
                    self.log_processing(
                        account_id=account.get("id"),
                        email_id=email_id,
                        message_id=message_id_header,
                        status="success",
                        processing_time=processing_time
                    )
                    
                    logger.info(f"Successfully processed email with subject: {email_content.subject}")
                    
                except Exception as e:
                    # Log error
                    error_message = str(e)
                    self.log_processing(
                        account_id=account.get("id"),
                        email_id=None,
                        message_id=message_id_header,
                        status="error",
                        error_message=error_message
                    )
                    
                    logger.error(f"Error processing email: {error_message}")
            
            # Update last checked timestamp
            self.update_last_checked(folder.get("id"))
    
    def poll_accounts(self) -> None:
        """Poll configured email accounts for new messages."""
        try:
            # Get configured accounts
            accounts = self.get_email_accounts()
            
            if not accounts:
                logger.warning("No email accounts configured. Skipping polling cycle.")
                return
            
            # Process each account
            for account in accounts:
                # Get configured folders for this account
                folders = self.get_account_folders(account.get("id"))
                
                if not folders:
                    logger.warning(f"No active folders configured for account {account.get('name')}. Skipping account.")
                    continue
                
                # Process each folder
                for folder in folders:
                    try:
                        self.process_emails(account, folder)
                    except Exception as e:
                        logger.error(f"Error processing folder {folder.get('folder_name')} for account {account.get('name')}: {str(e)}")
            
            logger.info("Completed email polling cycle")
                
        except Exception as e:
            logger.error(f"Error during polling cycle: {str(e)}")
    
    def _polling_thread(self) -> None:
        """Polling thread function."""
        logger.info("Starting email polling thread")
        
        while self.running:
            try:
                # Poll accounts
                self.poll_accounts()
                
                # Sleep until next polling cycle
                for _ in range(self.polling_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error in polling thread: {str(e)}")
                time.sleep(60)  # Wait a bit before retrying after an error
        
        logger.info("Email polling thread stopped")
    
    def start(self) -> bool:
        """Start the email fetcher service.
        
        Returns:
            True if started successfully, False if already running
        """
        if self.running:
            logger.warning("Email fetcher is already running")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._polling_thread)
        self.thread.daemon = True  # Thread will exit when main program exits
        self.thread.start()
        
        logger.info("Started email fetcher service")
        return True
    
    def stop(self) -> bool:
        """Stop the email fetcher service.
        
        Returns:
            True if stopped successfully, False if not running
        """
        if not self.running:
            logger.warning("Email fetcher is not running")
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=30)  # Wait up to 30 seconds for thread to exit
            self.thread = None
        
        logger.info("Stopped email fetcher service")
        return True