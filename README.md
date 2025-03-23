# Email Classification System

A comprehensive system for classifying, processing, and extracting information from emails. The system uses NLP and machine learning techniques to identify email types, extract relevant information, and generate formatted reports.

## Features

- **Email Classification**: Classify emails into predefined request types
- **Information Extraction**: Extract key data points from email content and attachments
- **Duplicate Detection**: Identify duplicate and similar emails using vector similarity
- **Report Generation**: Generate formatted reports (PDF, JSON) with extracted information
- **API Access**: Process emails via a RESTful API

## Architecture

The system follows a modular architecture with these main components:

- **Email Parser**: Parses raw emails into structured content
- **Classification Service**: Classifies emails and detects duplicates
- **Extraction Service**: Extracts relevant information based on email type
- **Reporting Service**: Generates reports in various formats
- **API**: Provides REST endpoints for email processing

## Installation

```bash
# Clone the repository
git clone https://github.com/Happyloopgit/email-classification-system.git
cd email-classification-system

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Usage

### Processing an Email

```python
from email_classification.email_parser import EmailParser
from email_classification.classification.classifier import EmailClassifier
from email_classification.extraction.extraction_service import ExtractionService
from email_classification.reporting.report_generator import ReportGenerator

# Parse email
parser = EmailParser()
email_content = parser.parse_file("path/to/email.eml")

# Classify email
classifier = EmailClassifier()
request_type, confidence = classifier.classify(email_content)
print(f"Email classified as {request_type} with confidence {confidence}")

# Extract information
# (In a real implementation, you would initialize these properly)
text_processor = TextProcessor()
document_processor = DocumentProcessor()
entity_processor = EntityProcessor()

extraction_service = ExtractionService(text_processor, document_processor, entity_processor)
extracted_data = extraction_service.extract(email_content, request_type)

# Generate report
report_generator = ReportGenerator()
pdf_path = report_generator.generate_pdf_report(extracted_data)
print(f"Generated PDF report at {pdf_path}")
```

### Using the API

```bash
# Start the API server
python -m email_classification.api.main
```

Then send a POST request to `/api/process-email` with the email content.

## Configuration

Configuration is managed through environment variables or a `.env` file:

```
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
VECTOR_STORE_DIR=data/vector_store
MODEL_PATH=models/classifier
```

## License

MIT
