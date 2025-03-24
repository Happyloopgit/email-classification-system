"""Repository for email operations."""

import json
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

from email_classification.database.supabase_client import SupabaseClient
from email_classification.extraction.email_content import EmailContent

logger = logging.getLogger(__name__)

class EmailRepository:
    """Repository for email-related database operations."""
    
    def __init__(self, supabase_client: Optional[SupabaseClient] = None):
        """Initialize the repository.
        
        Args:
            supabase_client: SupabaseClient instance. If None, creates a new one.
        """
        self.supabase = supabase_client or SupabaseClient()
        self.client = self.supabase.get_client()
        self.table_name = "emails"
        
        logger.info(f"Initialized EmailRepository with table: {self.table_name}")
    
    def _email_to_dict(self, email: EmailContent, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """Convert EmailContent object to dictionary for database storage.
        
        Args:
            email: EmailContent object
            embedding: Optional vector embedding of the email
            
        Returns:
            Dictionary representation of the email
        """
        return {
            "subject": email.subject,
            "from_address": email.from_address,
            "date": email.date,
            "plain_text": email.plain_text,
            "html_content": email.html_content,
            "attachments": json.dumps(email.attachments),
            "embedding": embedding,
            "created_at": datetime.now().isoformat()
        }
    
    def _dict_to_email(self, data: Dict[str, Any]) -> EmailContent:
        """Convert dictionary from database to EmailContent object.
        
        Args:
            data: Dictionary from database
            
        Returns:
            EmailContent object
        """
        # Parse attachments JSON
        attachments = []
        if data.get("attachments"):
            try:
                if isinstance(data["attachments"], str):
                    attachments = json.loads(data["attachments"])
                else:
                    attachments = data["attachments"]
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse attachments JSON: {data['attachments']}")
        
        return EmailContent(
            subject=data.get("subject", ""),
            from_address=data.get("from_address", ""),
            date=data.get("date", ""),
            plain_text=data.get("plain_text", ""),
            html_content=data.get("html_content", ""),
            attachments=attachments
        )
    
    def create(self, email: EmailContent, embedding: Optional[List[float]] = None) -> int:
        """Create a new email record.
        
        Args:
            email: EmailContent object to store
            embedding: Optional vector embedding of the email
            
        Returns:
            ID of the created record
        """
        try:
            email_data = self._email_to_dict(email, embedding)
            
            # Insert into Supabase
            result = self.client.table(self.table_name).insert(email_data).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                email_id = result['data'][0]['id']
                logger.info(f"Created email record with ID: {email_id}")
                return email_id
            else:
                logger.error(f"Failed to create email record: {result}")
                raise Exception("Failed to create email record")
                
        except Exception as e:
            logger.error(f"Error creating email record: {str(e)}")
            raise
    
    def get_by_id(self, email_id: int) -> Optional[EmailContent]:
        """Get email by ID.
        
        Args:
            email_id: Email record ID
            
        Returns:
            EmailContent object if found, None otherwise
        """
        try:
            result = self.client.table(self.table_name).select("*").eq("id", email_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                return self._dict_to_email(result['data'][0])
            else:
                logger.warning(f"Email with ID {email_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving email with ID {email_id}: {str(e)}")
            raise
    
    def find_similar_emails(
        self, 
        embedding: List[float], 
        threshold: float = 0.7, 
        max_results: int = 5
    ) -> List[Tuple[float, EmailContent]]:
        """Find similar emails using vector search.
        
        Args:
            embedding: Vector embedding to search for
            threshold: Similarity threshold (0-1)
            max_results: Maximum number of results to return
            
        Returns:
            List of tuples containing (similarity_score, EmailContent)
        """
        try:
            results = self.supabase.vector_search(
                table=self.table_name,
                column="embedding",
                query_embedding=embedding,
                match_threshold=threshold,
                match_count=max_results
            )
            
            # Convert results to EmailContent objects with similarity scores
            similar_emails = []
            for item in results:
                email = self._dict_to_email(item)
                similarity = item.get("similarity", 0.0)
                similar_emails.append((similarity, email))
                
            return similar_emails
            
        except Exception as e:
            logger.error(f"Error finding similar emails: {str(e)}")
            raise
    
    def update(self, email_id: int, data: Dict[str, Any]) -> bool:
        """Update an email record.
        
        Args:
            email_id: Email record ID
            data: Dictionary of fields to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            result = self.client.table(self.table_name).update(data).eq("id", email_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                logger.info(f"Updated email record with ID: {email_id}")
                return True
            else:
                logger.warning(f"Failed to update email with ID {email_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating email with ID {email_id}: {str(e)}")
            raise
    
    def delete(self, email_id: int) -> bool:
        """Delete an email record.
        
        Args:
            email_id: Email record ID
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            result = self.client.table(self.table_name).delete().eq("id", email_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                logger.info(f"Deleted email record with ID: {email_id}")
                return True
            else:
                logger.warning(f"Failed to delete email with ID {email_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting email with ID {email_id}: {str(e)}")
            raise