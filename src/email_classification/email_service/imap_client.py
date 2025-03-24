"""IMAP client for connecting to email servers."""

import imaplib
import email
import logging
from email.message import EmailMessage
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ImapClient:
    """IMAP client for interacting with email servers."""
    
    def __init__(
        self,
        server: str,
        port: int,
        username: str,
        password: str,
        use_ssl: bool = True
    ):
        """Initialize the IMAP client.
        
        Args:
            server: IMAP server address
            port: IMAP server port
            username: Email account username
            password: Email account password
            use_ssl: Whether to use SSL for connection
        """
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.connection = None
        
        logger.info(f"Initialized IMAP client for {username} on {server}:{port}")
    
    def connect(self) -> bool:
        """Connect to the IMAP server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create connection based on SSL setting
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                self.connection = imaplib.IMAP4(self.server, self.port)
            
            # Login to the server
            self.connection.login(self.username, self.password)
            logger.info(f"Connected to IMAP server: {self.server}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the IMAP server."""
        try:
            if self.connection:
                self.connection.logout()
                self.connection = None
                logger.info("Disconnected from IMAP server")
        except Exception as e:
            logger.error(f"Error disconnecting from IMAP server: {str(e)}")
    
    def list_folders(self) -> List[str]:
        """List available folders/mailboxes.
        
        Returns:
            List of folder names
        """
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            # Get folder list
            status, folders = self.connection.list()
            
            if status != 'OK':
                logger.error(f"Failed to list folders: {status}")
                return []
            
            # Parse folder names
            folder_names = []
            for folder in folders:
                if isinstance(folder, bytes):
                    parts = folder.decode().split(' "/" ')
                    if len(parts) > 1:
                        folder_name = parts[1].strip('"')
                        folder_names.append(folder_name)
            
            return folder_names
            
        except Exception as e:
            logger.error(f"Error listing folders: {str(e)}")
            return []
    
    def select_folder(self, folder_name: str) -> int:
        """Select a folder/mailbox for operations.
        
        Args:
            folder_name: Name of the folder to select
            
        Returns:
            Number of messages in the folder, -1 if error
        """
        try:
            if not self.connection:
                if not self.connect():
                    return -1
            
            # Select the folder
            status, data = self.connection.select(folder_name)
            
            if status != 'OK':
                logger.error(f"Failed to select folder {folder_name}: {status}")
                return -1
            
            # Return message count
            message_count = 0
            if data and data[0]:
                message_count = int(data[0])
            
            logger.info(f"Selected folder {folder_name} with {message_count} messages")
            return message_count
            
        except Exception as e:
            logger.error(f"Error selecting folder {folder_name}: {str(e)}")
            return -1
    
    def search_messages(self, criteria: str = "ALL", since_date: Optional[datetime] = None) -> List[str]:
        """Search for messages matching criteria.
        
        Args:
            criteria: IMAP search criteria
            since_date: Only return messages since this date
            
        Returns:
            List of message IDs
        """
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            # Build search query
            search_query = criteria
            if since_date:
                date_str = since_date.strftime("%d-%b-%Y")
                search_query = f'(SINCE "{date_str}" {criteria})'
            
            # Execute search
            status, data = self.connection.search(None, search_query)
            
            if status != 'OK':
                logger.error(f"Failed to search messages: {status}")
                return []
            
            # Parse message IDs
            message_ids = []
            if data and data[0]:
                message_ids = data[0].decode().split()
            
            logger.info(f"Found {len(message_ids)} messages matching criteria: {search_query}")
            return message_ids
            
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return []
    
    def fetch_message(self, message_id: str) -> Optional[EmailMessage]:
        """Fetch a message by ID.
        
        Args:
            message_id: Message ID to fetch
            
        Returns:
            EmailMessage object if successful, None otherwise
        """
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            # Fetch message data
            status, data = self.connection.fetch(message_id, "(RFC822)")
            
            if status != 'OK' or not data or not data[0]:
                logger.error(f"Failed to fetch message {message_id}: {status}")
                return None
            
            # Parse message
            message_data = data[0][1]
            message = email.message_from_bytes(message_data, policy=email.policy.default)
            
            return message
            
        except Exception as e:
            logger.error(f"Error fetching message {message_id}: {str(e)}")
            return None
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read.
        
        Args:
            message_id: Message ID to mark
            
        Returns:
            True if successful, False otherwise
        """
        return self._set_flags(message_id, "\\Seen")
    
    def mark_as_flagged(self, message_id: str) -> bool:
        """Mark a message as flagged/important.
        
        Args:
            message_id: Message ID to mark
            
        Returns:
            True if successful, False otherwise
        """
        return self._set_flags(message_id, "\\Flagged")
    
    def _set_flags(self, message_id: str, flag: str) -> bool:
        """Set flags on a message.
        
        Args:
            message_id: Message ID to modify
            flag: IMAP flag to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            # Set the flag
            status, data = self.connection.store(message_id, "+FLAGS", flag)
            
            if status != 'OK':
                logger.error(f"Failed to set flag {flag} on message {message_id}: {status}")
                return False
            
            logger.info(f"Set flag {flag} on message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting flag {flag} on message {message_id}: {str(e)}")
            return False
    
    def move_to_folder(self, message_id: str, destination_folder: str) -> bool:
        """Move a message to another folder.
        
        Args:
            message_id: Message ID to move
            destination_folder: Destination folder name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            # Copy the message to the destination folder
            status, data = self.connection.copy(message_id, destination_folder)
            
            if status != 'OK':
                logger.error(f"Failed to copy message {message_id} to {destination_folder}: {status}")
                return False
            
            # Mark the original message for deletion
            status, data = self.connection.store(message_id, "+FLAGS", "\\Deleted")
            
            if status != 'OK':
                logger.error(f"Failed to mark message {message_id} for deletion: {status}")
                return False
            
            # Expunge to actually delete the message
            status, data = self.connection.expunge()
            
            if status != 'OK':
                logger.error(f"Failed to expunge deleted messages: {status}")
                return False
            
            logger.info(f"Moved message {message_id} to folder {destination_folder}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving message {message_id} to folder {destination_folder}: {str(e)}")
            return False
    
    def __enter__(self):
        """Context manager support - connect on enter."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support - disconnect on exit."""
        self.disconnect()