#!/usr/bin/env python
"""Script to create a sample PDF invoice for testing."""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

# Ensure the examples directory exists
os.makedirs("examples", exist_ok=True)

# Define the output PDF file
pdf_file = "examples/sample_invoice.pdf"

# Create a PDF document
doc = SimpleDocTemplate(pdf_file, pagesize=letter)
styles = getSampleStyleSheet()

# Define custom styles
title_style = ParagraphStyle(
    'Title',
    parent=styles['Heading1'],
    fontSize=16,
    alignment=1,  # Center alignment
    spaceAfter=0.25*inch
)

header_style = ParagraphStyle(
    'Header',
    parent=styles['Heading2'],
    fontSize=12,
)

normal_style = styles["Normal"]

# Create content elements
elements = []

# Title
elements.append(Paragraph("INVOICE", title_style))
elements.append(Spacer(1, 0.25*inch))

# Company info
company_info = [
    ["Example Company"],
    ["123 Business Street"],
    ["City, State 12345"],
    ["Phone: 555-987-6543"],
    ["Email: billing@example.com"],
]
company_table = Table(company_info)
company_table.setStyle(TableStyle([
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
]))
elements.append(company_table)
elements.append(Spacer(1, 0.25*inch))

# Invoice info
invoice_info = [
    ["Invoice Number:", "INV-2023-4567"],
    ["Order Number:", "ORD-78901"],
    ["Date:", "September 15, 2023"],
    ["Due Date:", "October 15, 2023"],
    ["Customer ID:", "CUST-001234"],
]
invoice_table = Table(invoice_info, colWidths=[1.5*inch, 3*inch])
invoice_table.setStyle(TableStyle([
    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
]))
elements.append(invoice_table)
elements.append(Spacer(1, 0.25*inch))

# Items header
elements.append(Paragraph("Invoice Items", header_style))
elements.append(Spacer(1, 0.1*inch))

# Invoice items
data = [
    ["Description", "Quantity", "Unit Price", "Total"],
    ["Product A - Premium Widget", "2", "$500.00", "$1,000.00"],
    ["Product B - Enterprise License", "1", "$1,200.00", "$1,200.00"],
    ["Service - Installation", "3", "$45.00", "$135.00"],
    ["Service - Support (1 year)", "1", "$10.67", "$10.67"],
]

# Create the items table
items_table = Table(data, colWidths=[3*inch, 1*inch, 1.25*inch, 1.25*inch])
items_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
elements.append(items_table)
elements.append(Spacer(1, 0.25*inch))

# Totals
totals_data = [
    ["", "", "Subtotal:", "$2,345.67"],
    ["", "", "Tax (0%):", "$0.00"],
    ["", "", "Total Due:", "$2,345.67"],
]
totals_table = Table(totals_data, colWidths=[3*inch, 1*inch, 1.25*inch, 1.25*inch])
totals_table.setStyle(TableStyle([
    ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
    ('LINEABOVE', (2, -1), (3, -1), 1, colors.black),
    ('LINEBELOW', (2, -1), (3, -1), 1, colors.black),
]))
elements.append(totals_table)
elements.append(Spacer(1, 0.5*inch))

# Payment info
payment_info = """
<b>Payment Information:</b><br/>
Please make payment by the due date using one of the following methods:<br/>
- Credit Card (online at example.com/pay)<br/>
- Bank Transfer to Account #12345678<br/>
- Check payable to "Example Company"<br/><br/>
For questions regarding this invoice, please contact billing@example.com or call 555-123-4567.
"""
payment_paragraph = Paragraph(payment_info, normal_style)
elements.append(payment_paragraph)

# Build the PDF
doc.build(elements)

print(f"Sample invoice created at: {pdf_file}")

if __name__ == "__main__":
    pass