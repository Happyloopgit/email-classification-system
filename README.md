# Email Classification System

A system for classifying emails, extracting relevant information based on the request type, and detecting duplicates using vector similarity search.

## Features

- Email classification into multiple request types
- Information extraction based on email content and request type
- Document processing (attachments, PDF, Word, etc.)
- Duplicate detection using vector similarity search
- REST API for integration with other systems

## API Documentation

The system provides a RESTful API with the following endpoints:

### Classify Email

```
POST /api/v1/classify
```

Classifies an email, extracts relevant information, and checks for duplicates.

**Parameters:**
- `email_content` (string, required): The body of the email
- `email_subject` (string, required): The subject of the email
- `email_from` (string, required): The sender of the email
- `email_date` (string, required): The date the email was sent
- `attachment` (file, optional): Optional attachment file

**Response:**
```json
{
  "request_type": "string",
  "confidence": 0.95,
  "extracted_fields": {
    "field1": "value1",
    "field2": "value2"
  },
  "is_duplicate": false,
  "similar_emails": []
}
```

### Get Request Types

```
GET /api/v1/request-types
```

Returns a list of supported request types.

**Response:**
```json
[
  "information_request",
  "change_request",
  "complaint",
  "feedback",
  "account_update",
  "technical_support",
  "billing_inquiry"
]
```

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: 
   - Windows: `venv\Scripts\activate`
   - Unix/macOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure the settings
6. If using OCR functionality, install Tesseract OCR:
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

## Usage

### Running the API Server

```bash
python -m src.email_classification.main
```

This will start the FastAPI server on the host and port specified in your `.env` file (defaults to http://0.0.0.0:8000).

You can access the API documentation at http://localhost:8000/docs.

### Example API Call

```python
import requests

url = "http://localhost:8000/api/v1/classify"
files = {
    'attachment': ('invoice.pdf', open('invoice.pdf', 'rb'), 'application/pdf')
}
data = {
    'email_content': 'Please find attached invoice for your recent purchase.',
    'email_subject': 'Invoice for Order #12345',
    'email_from': 'billing@example.com',
    'email_date': '2023-09-15T14:30:00Z'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## Configuration

The system can be configured via environment variables or the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| API_HOST | API server host | 0.0.0.0 |
| API_PORT | API server port | 8000 |
| LOG_LEVEL | Logging level | info |
| API_RELOAD | Enable auto-reload | false |
| CLASSIFIER_MODEL | Model for email classification | all-MiniLM-L6-v2 |
| VECTOR_STORE_MODEL | Model for vector store | all-MiniLM-L6-v2 |
| SIMILARITY_THRESHOLD | Threshold for duplicate detection | 0.9 |
| EXTRACTION_LLM_MODEL | LLM model for extraction | gpt-4 |
| OCR_ENABLED | Enable OCR for documents | true |
| LANGUAGE | Language for extraction | en |
| OPENAI_API_KEY | OpenAI API key | - |

## License

[MIT License](LICENSE)