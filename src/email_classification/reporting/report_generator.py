"""Report generation for extracted and classified emails."""

from typing import Dict, Any, List, Optional
import logging
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates reports from extracted email data."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize report generator.
        
        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        logger.info(f"Initialized ReportGenerator with output directory: {output_dir}")
    
    def generate_json_report(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Generate JSON report from extracted data.
        
        Args:
            data: The extracted data to include in the report
            filename: Optional filename for the report
            
        Returns:
            Path to the generated report file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"report_{timestamp}.json"
                
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Generated JSON report: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error generating JSON report: {str(e)}")
            raise
    
    def generate_pdf_report(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Generate PDF report from extracted data.
        
        Args:
            data: The extracted data to include in the report
            filename: Optional filename for the report
            
        Returns:
            Path to the generated report file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"report_{timestamp}.pdf"
                
            file_path = os.path.join(self.output_dir, filename)
            
            # Create the PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Title
            title_style = self.styles['Heading1']
            elements.append(Paragraph("Email Classification Report", title_style))
            elements.append(Spacer(1, 12))
            
            # Request type information
            request_type = data.get("request_type", "Unknown")
            elements.append(Paragraph(f"Request Type: {request_type}", self.styles['Heading2']))
            elements.append(Spacer(1, 6))
            
            # Create a table for the data
            table_data = []
            table_data.append(["Field", "Value"])
            
            # Add standard fields
            for key, value in data.items():
                if key not in ["request_type", "entities"] and not isinstance(value, (dict, list)):
                    table_data.append([key, str(value)])
            
            # Create and style the table
            table = Table(table_data, colWidths=[200, 300])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 12))
            
            # Add entities if present
            if "entities" in data and isinstance(data["entities"], list) and data["entities"]:
                elements.append(Paragraph("Extracted Entities", self.styles['Heading2']))
                elements.append(Spacer(1, 6))
                
                entity_data = [["Entity", "Type", "Value"]]
                for entity in data["entities"]:
                    if isinstance(entity, dict):
                        entity_data.append([
                            entity.get("name", ""),
                            entity.get("type", ""),
                            entity.get("value", "")
                        ])
                
                entity_table = Table(entity_data, colWidths=[150, 150, 200])
                entity_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (2, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (2, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(entity_table)
            
            # Build the PDF
            doc.build(elements)
            
            logger.info(f"Generated PDF report: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise