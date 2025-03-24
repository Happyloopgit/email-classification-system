"""Repository for report operations."""

import json
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

from email_classification.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class ReportRepository:
    """Repository for report-related database operations."""
    
    def __init__(self, supabase_client: Optional[SupabaseClient] = None):
        """Initialize the repository.
        
        Args:
            supabase_client: SupabaseClient instance. If None, creates a new one.
        """
        self.supabase = supabase_client or SupabaseClient()
        self.client = self.supabase.get_client()
        self.table_name = "reports"
        
        logger.info(f"Initialized ReportRepository with table: {self.table_name}")
    
    def create(self, email_id: int, report_type: str, file_path: str, metadata: Dict[str, Any] = None) -> int:
        """Create a new report record.
        
        Args:
            email_id: Email record ID
            report_type: Type of report (pdf, json, etc.)
            file_path: Path to the generated report file
            metadata: Optional metadata about the report
            
        Returns:
            ID of the created record
        """
        try:
            report_data = {
                "email_id": email_id,
                "report_type": report_type,
                "file_path": file_path,
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.now().isoformat()
            }
            
            # Insert into Supabase
            result = self.client.table(self.table_name).insert(report_data).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                report_id = result['data'][0]['id']
                logger.info(f"Created report record with ID: {report_id}")
                return report_id
            else:
                logger.error(f"Failed to create report record: {result}")
                raise Exception("Failed to create report record")
                
        except Exception as e:
            logger.error(f"Error creating report record: {str(e)}")
            raise
    
    def get_by_email_id(self, email_id: int) -> List[Dict[str, Any]]:
        """Get reports by email ID.
        
        Args:
            email_id: Email record ID
            
        Returns:
            List of report records for the email
        """
        try:
            result = self.client.table(self.table_name).select("*").eq("email_id", email_id).execute()
            
            if 'data' in result and result['data']:
                data_list = result['data']
                
                # Parse metadata JSON for each record
                for item in data_list:
                    if "metadata" in item and item["metadata"]:
                        try:
                            if isinstance(item["metadata"], str):
                                item["metadata"] = json.loads(item["metadata"])
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse metadata JSON for report ID {item.get('id')}")
                
                return data_list
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving reports for email ID {email_id}: {str(e)}")
            raise
    
    def get_by_type(self, report_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get reports by type.
        
        Args:
            report_type: Type of report (pdf, json, etc.)
            limit: Maximum number of records to return
            
        Returns:
            List of report records of the specified type
        """
        try:
            result = self.client.table(self.table_name).select("*") \
                .eq("report_type", report_type) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            if 'data' in result and result['data']:
                data_list = result['data']
                
                # Parse metadata JSON for each record
                for item in data_list:
                    if "metadata" in item and item["metadata"]:
                        try:
                            if isinstance(item["metadata"], str):
                                item["metadata"] = json.loads(item["metadata"])
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse metadata JSON for report ID {item.get('id')}")
                
                return data_list
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving reports of type {report_type}: {str(e)}")
            raise
    
    def update(self, report_id: int, data: Dict[str, Any]) -> bool:
        """Update a report record.
        
        Args:
            report_id: Report record ID
            data: Dictionary of fields to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # If metadata is in the update, convert it to JSON string
            if "metadata" in data and not isinstance(data["metadata"], str):
                data["metadata"] = json.dumps(data["metadata"])
                
            result = self.client.table(self.table_name).update(data).eq("id", report_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                logger.info(f"Updated report record with ID: {report_id}")
                return True
            else:
                logger.warning(f"Failed to update report with ID {report_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating report with ID {report_id}: {str(e)}")
            raise
    
    def delete(self, report_id: int) -> bool:
        """Delete a report record.
        
        Args:
            report_id: Report record ID
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            result = self.client.table(self.table_name).delete().eq("id", report_id).execute()
            
            if 'data' in result and result['data'] and len(result['data']) > 0:
                logger.info(f"Deleted report record with ID: {report_id}")
                return True
            else:
                logger.warning(f"Failed to delete report with ID {report_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting report with ID {report_id}: {str(e)}")
            raise