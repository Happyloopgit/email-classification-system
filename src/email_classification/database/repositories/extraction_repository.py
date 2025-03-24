"""Repository for extraction operations."""

import json
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

from email_classification.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class ExtractionRepository:
    """Repository for extraction-related database operations."""
    
    def __init__(self, supabase_client: Optional[SupabaseClient] = None):
        """Initialize the repository.
        
        Args:
            supabase_client: SupabaseClient instance. If None, creates a new one.
        """
        self.supabase = supabase_client or SupabaseClient()
        self.client = self.supabase.get_client()
        self.table_name = "extractions"
        
        logger.info(f"Initialized ExtractionRepository with table: {self.table_name}")
    
    def create(self, email_id: int, extracted_data: Dict[str, Any]) -> int:
        """Create a new extraction record.
        
        Args:
            email_id: Email record ID
            extracted_data: Dictionary of extracted data
            
        Returns:
            ID of the created record
        """
        try:
            # Extract common fields from the data
            amount = extracted_data.get("amount", None)
            reference_number = extracted_data.get("reference_number", None)
            account_number = extracted_data.get("account_number", None)
            
            extraction_data = {
                "email_id": email_id,
                "amount": amount,
                "reference_number": reference_number,
                "account_number": account_number,
                "extracted_data": json.dumps(extracted_data),
                "created_at": datetime.now().isoformat()
            }
            
            # Insert into Supabase
            result = self.client.table(self.table_name).insert(extraction_data).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                extraction_id = result['data'][0]['id']
                logger.info(f"Created extraction record with ID: {extraction_id}")
                return extraction_id
            else:
                logger.error(f"Failed to create extraction record: {result}")
                raise Exception("Failed to create extraction record")
                
        except Exception as e:
            logger.error(f"Error creating extraction record: {str(e)}")
            raise
    
    def get_by_email_id(self, email_id: int) -> Optional[Dict[str, Any]]:
        """Get extraction by email ID.
        
        Args:
            email_id: Email record ID
            
        Returns:
            Extraction record if found, None otherwise
        """
        try:
            result = self.client.table(self.table_name).select("*").eq("email_id", email_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                data = result['data'][0]
                
                # Parse the extracted_data JSON
                if "extracted_data" in data and data["extracted_data"]:
                    try:
                        if isinstance(data["extracted_data"], str):
                            data["extracted_data"] = json.loads(data["extracted_data"])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse extracted_data JSON for email ID {email_id}")
                
                return data
            else:
                logger.warning(f"Extraction for email ID {email_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving extraction for email ID {email_id}: {str(e)}")
            raise
    
    def search_by_fields(self, field_values: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Search extractions by field values.
        
        Args:
            field_values: Dictionary of field-value pairs to search for
            limit: Maximum number of records to return
            
        Returns:
            List of extraction records matching the criteria
        """
        try:
            query = self.client.table(self.table_name).select("*")
            
            # Add filters for each field-value pair
            for field, value in field_values.items():
                if field in ["amount", "reference_number", "account_number"]:
                    query = query.eq(field, value)
            
            # Execute the query with limit
            result = query.limit(limit).execute()
            
            if 'data' in result and result['data']:
                data_list = result['data']
                
                # Parse extracted_data JSON for each record
                for item in data_list:
                    if "extracted_data" in item and item["extracted_data"]:
                        try:
                            if isinstance(item["extracted_data"], str):
                                item["extracted_data"] = json.loads(item["extracted_data"])
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse extracted_data JSON for record ID {item.get('id')}")
                
                return data_list
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error searching extractions by fields: {str(e)}")
            raise
    
    def update(self, extraction_id: int, data: Dict[str, Any]) -> bool:
        """Update an extraction record.
        
        Args:
            extraction_id: Extraction record ID
            data: Dictionary of fields to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # If extracted_data is in the update, convert it to JSON string
            if "extracted_data" in data and not isinstance(data["extracted_data"], str):
                data["extracted_data"] = json.dumps(data["extracted_data"])
                
            result = self.client.table(self.table_name).update(data).eq("id", extraction_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                logger.info(f"Updated extraction record with ID: {extraction_id}")
                return True
            else:
                logger.warning(f"Failed to update extraction with ID {extraction_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating extraction with ID {extraction_id}: {str(e)}")
            raise
    
    def delete(self, extraction_id: int) -> bool:
        """Delete an extraction record.
        
        Args:
            extraction_id: Extraction record ID
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            result = self.client.table(self.table_name).delete().eq("id", extraction_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                logger.info(f"Deleted extraction record with ID: {extraction_id}")
                return True
            else:
                logger.warning(f"Failed to delete extraction with ID {extraction_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting extraction with ID {extraction_id}: {str(e)}")
            raise