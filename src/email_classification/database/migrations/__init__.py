"""Database migration scripts."""

import logging
from pathlib import Path
from typing import List, Dict, Any

from email_classification.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

def run_migrations() -> bool:
    """Run all database migrations.
    
    Returns:
        True if migrations were successful, False otherwise
    """
    try:
        migrations_path = Path(__file__).parent
        migration_files = sorted([f for f in migrations_path.glob("*.sql") if f.is_file()])
        
        if not migration_files:
            logger.warning("No migration files found.")
            return True
        
        logger.info(f"Found {len(migration_files)} migration files.")
        
        # Create migrations table if it doesn't exist
        supabase = SupabaseClient()
        _ensure_migrations_table(supabase)
        
        # Get applied migrations
        applied_migrations = _get_applied_migrations(supabase)
        applied_filenames = [m["filename"] for m in applied_migrations]
        
        # Run pending migrations
        for migration_file in migration_files:
            filename = migration_file.name
            if filename not in applied_filenames:
                logger.info(f"Running migration: {filename}")
                
                # Read SQL content
                sql_content = migration_file.read_text()
                
                # Execute migration
                supabase.execute_query(sql_content)
                
                # Mark migration as applied
                _mark_migration_applied(supabase, filename)
                
                logger.info(f"Migration {filename} applied successfully.")
        
        logger.info("All migrations completed successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        return False

def _ensure_migrations_table(supabase: SupabaseClient) -> None:
    """Ensure the migrations table exists.
    
    Args:
        supabase: SupabaseClient instance
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS migrations (
        id SERIAL PRIMARY KEY,
        filename TEXT NOT NULL UNIQUE,
        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    supabase.execute_query(create_table_sql)

def _get_applied_migrations(supabase: SupabaseClient) -> List[Dict[str, Any]]:
    """Get a list of applied migrations.
    
    Args:
        supabase: SupabaseClient instance
        
    Returns:
        List of applied migration records
    """
    query = "SELECT * FROM migrations ORDER BY applied_at ASC;"
    return supabase.execute_query(query)

def _mark_migration_applied(supabase: SupabaseClient, filename: str) -> None:
    """Mark a migration as applied.
    
    Args:
        supabase: SupabaseClient instance
        filename: Migration filename
    """
    query = """
    INSERT INTO migrations (filename) VALUES ($1);
    """
    
    supabase.execute_query(query, {"1": filename})