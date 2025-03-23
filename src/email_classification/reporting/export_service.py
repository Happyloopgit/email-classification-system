"""Service for exporting processed emails and reports."""

from typing import Dict, Any, List, Optional
import logging
import os
import csv
from datetime import datetime

from email_classification.reporting.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

class ExportService:
    """Service for exporting processed emails and generating reports."""
    
    def __init__(self, report_generator: ReportGenerator, export_dir: str = "exports"):
        """Initialize export service.
        
        Args:
            report_generator: ReportGenerator instance for creating reports
            export_dir: Directory to save exported data
        """
        self.report_generator = report_generator
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        logger.info(f"Initialized ExportService with export directory: {export_dir}")
    
    def export_to_csv(self, data_list: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Export data to CSV file.
        
        Args:
            data_list: List of data dictionaries to export
            filename: Optional filename for the CSV file
            
        Returns:
            Path to the exported CSV file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_{timestamp}.csv"
                
            file_path = os.path.join(self.export_dir, filename)
            
            # Get all unique keys from all dictionaries
            fieldnames = set()
            for data in data_list:
                fieldnames.update(data.keys())
            
            fieldnames = sorted(list(fieldnames))
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for data in data_list:
                    writer.writerow(data)
            
            logger.info(f"Exported data to CSV: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise
    
    def generate_report(self, data: Dict[str, Any], format_type: str = "pdf") -> str:
        """Generate a report from extracted data.
        
        Args:
            data: The data to include in the report
            format_type: Report format ("pdf" or "json")
            
        Returns:
            Path to the generated report file
        """
        try:
            if format_type.lower() == "pdf":
                return self.report_generator.generate_pdf_report(data)
            elif format_type.lower() == "json":
                return self.report_generator.generate_json_report(data)
            else:
                raise ValueError(f"Unsupported report format: {format_type}")
        
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise
    
    def batch_export(self, data_list: List[Dict[str, Any]], format_type: str = "csv") -> str:
        """Export a batch of processed emails.
        
        Args:
            data_list: List of processed email data
            format_type: Export format ("csv" or "json")
            
        Returns:
            Path to the exported file
        """
        try:
            if format_type.lower() == "csv":
                return self.export_to_csv(data_list)
            elif format_type.lower() == "json":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"batch_export_{timestamp}.json"
                return self.report_generator.generate_json_report(
                    {"batch_size": len(data_list), "items": data_list},
                    filename=filename
                )
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
        
        except Exception as e:
            logger.error(f"Error in batch export: {str(e)}")
            raise