"""Supabase client for database operations."""

import os
import logging
from typing import Dict, Any, List, Optional, Union

from supabase import create_client, Client
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Manages Supabase connection and operations."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one client instance."""
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize Supabase client."""
        if self._initialized:
            return
            
        # Load environment variables from .env file if present
        load_dotenv()
        
        # Get Supabase credentials from environment variables
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            error_msg = "Supabase URL and key must be provided in environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            # Initialize the Supabase client
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client initialized successfully")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    def get_client(self) -> Client:
        """Get the Supabase client instance."""
        return self.client
    
    def execute_query(self, query: str, values: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a raw SQL query.
        
        Args:
            query: SQL query string
            values: Dictionary of values to use in the query
            
        Returns:
            Query result
        """
        try:
            result = self.client.rpc(
                "execute_sql", 
                {"query": query, "params": values or {}}
            ).execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Failed to execute query: {str(e)}")
            raise
    
    def vector_search(
        self, 
        table: str, 
        column: str, 
        query_embedding: List[float],
        match_threshold: float = 0.7,
        match_count: int = 10,
        filter_string: str = ""
    ) -> List[Dict[str, Any]]:
        """Perform a vector similarity search.
        
        Args:
            table: Table name
            column: Column containing vector embeddings
            query_embedding: Vector to search for
            match_threshold: Minimum similarity threshold
            match_count: Maximum number of matches to return
            filter_string: Additional filter conditions
            
        Returns:
            List of matching records with similarity scores
        """
        try:
            # Construct the SQL query for vector search
            query = f"""
            SELECT *, 1 - ({column} <=> $1) as similarity
            FROM {table}
            WHERE 1 - ({column} <=> $1) > $2
            {filter_string}
            ORDER BY similarity DESC
            LIMIT $3
            """
            
            # Execute the query
            result = self.execute_query(
                query,
                {
                    "1": query_embedding,
                    "2": match_threshold,
                    "3": match_count
                }
            )
            
            return result
        except Exception as e:
            logger.error(f"Failed to perform vector search: {str(e)}")
            raise