# Email Classification System

A comprehensive system for classifying, processing, and extracting information from emails. The system uses NLP and machine learning techniques to identify email types, extract relevant information, and generate formatted reports.

## Features

- **Email Classification**: Classify emails into predefined request types
- **Information Extraction**: Extract key data points from email content and attachments
- **Duplicate Detection**: Identify duplicate and similar emails using vector similarity
- **Report Generation**: Generate formatted reports (PDF, JSON) with extracted information
- **Email Integration**: Connect to email servers via IMAP and send responses via SMTP
- **Supabase Backend**: Store and retrieve data using PostgreSQL with vector search capabilities
- **LLM Integration**: Use OpenAI or Anthropic models for advanced text processing
- **API Access**: Process emails via a RESTful API

## Architecture

The system follows a modular architecture with these main components:

- **Email Parser**: Parses raw emails into structured content
- **Email Service**: Connects to email servers to fetch and send emails
- **Classification Service**: Classifies emails and detects duplicates
- **Extraction Service**: Extracts relevant information based on email type
- **LLM Service**: Integrates with language models for advanced text processing
- **Reporting Service**: Generates reports in various formats
- **Database Layer**: Stores and retrieves data using Supabase
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

## Configuration

Configuration is managed through environment variables or a `.env` file. Copy the example configuration file and modify it:

```bash
cp .env.example .env
```

Edit the `.env` file to set your configuration:

```
# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# LLM Configuration
LLM_PROVIDER=openai  # options: openai, anthropic
LLM_MODEL=gpt-4      # or claude-3-opus, etc.
LLM_API_KEY=your-api-key

# Email Configuration
EMAIL_SERVER=imap.example.com
EMAIL_PORT=993
EMAIL_USE_SSL=True
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_password
EMAIL_POLLING_INTERVAL=300  # seconds

# SMTP Configuration
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_password

# Storage Paths
VECTOR_STORE_DIR=data/vector_store
ATTACHMENTS_DIR=attachments
REPORTS_DIR=reports
EXPORTS_DIR=exports
```

## Database Setup

The system uses Supabase as its database backend. Follow these steps to set up the database:

1. Create a Supabase account and project at [supabase.com](https://supabase.com)
2. Enable the vector extension in your Supabase project
3. Copy your project URL and API key to the `.env` file
4. Run the database migrations:

```bash
python -m email_classification.database.migrate
```

## Email Service Configuration

### Configuring Email Accounts

You can configure multiple email accounts in the database. Use the API or database interface to add accounts:

```sql
INSERT INTO email_accounts (name, server, port, use_ssl, username, password)
VALUES ('support', 'imap.example.com', 993, true, 'support@example.com', 'your-password');
```

### Configuring Email Folders

For each account, configure which folders to monitor:

```sql
INSERT INTO email_folders (account_id, folder_name, is_active)
VALUES (1, 'INBOX', true);
```

## LLM Configuration

### Changing LLM Providers

The system supports different LLM providers. Configure in your `.env` file:

```
# LLM settings
LLM_PROVIDER=openai  # options: openai, anthropic
LLM_MODEL=gpt-4      # or claude-3-opus, etc.
LLM_API_KEY=your_api_key_here
```

## Usage

### Processing an Email

```python
from email_classification.email_parser import EmailParser
from email_classification.classification.classifier import EmailClassifier
from email_classification.duplicate_detection.vector_store import EmailVectorStore
from email_classification.classification.classification_service import ClassificationService
from email_classification.extraction.processors import TextProcessor, DocumentProcessor, EntityProcessor
from email_classification.extraction.extraction_service import ExtractionService
from email_classification.reporting.report_generator import ReportGenerator

# Parse email
parser = EmailParser()
email_content = parser.parse_file("path/to/email.eml")

# Classify email
classifier = EmailClassifier()
vector_store = EmailVectorStore()
classification_service = ClassificationService(classifier, vector_store)
classification_result = classification_service.process_email(email_content)

request_type = classification_result["request_type"]
print(f"Email classified as {request_type} with confidence {classification_result['confidence']}")

# Extract information
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

### Fetching Emails Automatically

```python
from email_classification.email_parser import EmailParser
from email_classification.email_service import EmailFetcher
from email_classification.classification.classification_service import ClassificationService

# Create email processor pipeline
def process_email(email_content):
    # Your email processing logic here
    return {"status": "processed"}

# Initialize fetcher
parser = EmailParser()
fetcher = EmailFetcher(parser)

# Register processor
fetcher.register_processor(process_email)

# Start fetching emails
fetcher.start()

# To stop fetching
# fetcher.stop()
```

### Using the API

```bash
# Start the API server
python -m email_classification.api.main
```

Then send a POST request to `/api/process-email` with the email content.

## License

MIT
