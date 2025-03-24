"""Repository for classification operations."""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

from email_classification.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class ClassificationRepository:
    """Repository for classification-related database operations."""
    
    def __init__(self, supabase_client: Optional[SupabaseClient] = None):
        """Initialize the repository.
        
        Args:
            supabase_client: SupabaseClient instance. If None, creates a new one.
        """
        self.supabase = supabase_client or SupabaseClient()
        self.client = self.supabase.get_client()
        self.table_name = "classifications"
        
        logger.info(f"Initialized ClassificationRepository with table: {self.table_name}")
    
    def create(self, email_id: int, request_type: str, confidence: float, is_duplicate: bool) -> int:
        """Create a new classification record.
        
        Args:
            email_id: Email record ID
            request_type: Classified request type
            confidence: Classification confidence score
            is_duplicate: Whether the email is a duplicate
            
        Returns:
            ID of the created record
        """
        try:
            classification_data = {
                "email_id": email_id,
                "request_type": request_type,
                "confidence": confidence,
                "is_duplicate": is_duplicate,
                "created_at": datetime.now().isoformat()
            }
            
            # Insert into Supabase
            result = self.client.table(self.table_name).insert(classification_data).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                classification_id = result['data'][0]['id']
                logger.info(f"Created classification record with ID: {classification_id}")
                return classification_id
            else:
                logger.error(f"Failed to create classification record: {result}")
                raise Exception("Failed to create classification record")
                
        except Exception as e:
            logger.error(f"Error creating classification record: {str(e)}")
            raise
    
    def get_by_email_id(self, email_id: int) -> Optional[Dict[str, Any]]:
        """Get classification by email ID.
        
        Args:
            email_id: Email record ID
            
        Returns:
            Classification record if found, None otherwise
        """
        try:
            result = self.client.table(self.table_name).select("*").eq("email_id", email_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                return result['data'][0]
            else:
                logger.warning(f"Classification for email ID {email_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving classification for email ID {email_id}: {str(e)}")
            raise
    
    def get_by_request_type(self, request_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get classifications by request type.
        
        Args:
            request_type: Type of request to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of classification records
        """
        try:
            result = self.client.table(self.table_name).select("*") \
                .eq("request_type", request_type) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            if 'data' in result and result['data']:
                return result['data']
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving classifications for request type {request_type}: {str(e)}")
            raise
    
    def update(self, classification_id: int, data: Dict[str, Any]) -> bool:
        """Update a classification record.
        
        Args:
            classification_id: Classification record ID
            data: Dictionary of fields to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            result = self.client.table(self.table_name).update(data).eq("id", classification_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                logger.info(f"Updated classification record with ID: {classification_id}")
                return True
            else:
                logger.warning(f"Failed to update classification with ID {classification_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating classification with ID {classification_id}: {str(e)}")
            raise
    
    def delete(self, classification_id: int) -> bool:
        """Delete a classification record.
        
        Args:
            classification_id: Classification record ID
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            result = self.client.table(self.table_name).delete().eq("id", classification_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                logger.info(f"Deleted classification record with ID: {classification_id}")
                return True
            else:
                logger.warning(f"Failed to delete classification with ID {classification_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting classification with ID {classification_id}: {str(e)}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get classification statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            query = """
            SELECT 
                request_type, 
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM classifications
            GROUP BY request_type
            ORDER BY count DESC
            """
            
            result = self.supabase.execute_query(query)
            
            # Count duplicates
            duplicate_query = """
            SELECT COUNT(*) as duplicate_count
            FROM classifications
            WHERE is_duplicate = TRUE
            """
            
            duplicate_result = self.supabase.execute_query(duplicate_query)
            duplicate_count = 0
            if duplicate_result and len(duplicate_result) > 0:
                duplicate_count = duplicate_result[0].get("duplicate_count", 0)
            
            return {
                "by_request_type": result,
                "duplicate_count": duplicate_count,
                "total_count": sum(item.get("count", 0) for item in result)
            }
                
        except Exception as e:
            logger.error(f"Error retrieving classification statistics: {str(e)}")
            raise