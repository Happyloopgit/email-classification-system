"""Predefined prompts for LLM interactions."""

from typing import Dict, Any, List

# Email classification prompts
EMAIL_CLASSIFICATION_PROMPT = """
Analyze the following email and classify it into exactly one of these categories:
{categories}

For each category, assign a confidence score between 0.0 and 1.0.

Email Subject: {subject}

Email Body:
{body}

Your output should be in JSON format with category names as keys and confidence scores as values.
"""

# Entity extraction prompts
ENTITY_EXTRACTION_PROMPT = """
Extract the following types of entities from the email text:
{entity_types}

Email Subject: {subject}

Email Body:
{body}

Format your response as a JSON array of objects, where each object has:
- 'type': The entity type
- 'value': The extracted value
- 'context': A brief snippet of text surrounding the entity (optional)
"""

# Request-specific extraction prompts
REIMBURSEMENT_EXTRACTION_PROMPT = """
This is a reimbursement request email. Extract the following information:
- amount: The amount to be reimbursed (with currency symbol if available)
- date: The date of the expense
- expense_type: The type of expense (e.g., travel, supplies, etc.)
- payee: The person to be reimbursed
- reference_number: Any reference number mentioned
- account_number: Any account number for the reimbursement

Email Subject: {subject}

Email Body:
{body}

Provide your answer in JSON format with these fields.
"""

INVOICE_PAYMENT_EXTRACTION_PROMPT = """
This is an invoice payment request email. Extract the following information:
- invoice_number: The invoice ID or number
- amount: The payment amount (with currency symbol if available)
- due_date: The payment due date
- vendor: The vendor or company issuing the invoice
- reference_number: Any reference number mentioned
- account_number: Any account number for the payment

Email Subject: {subject}

Email Body:
{body}

Provide your answer in JSON format with these fields.
"""

ACCOUNT_INQUIRY_EXTRACTION_PROMPT = """
This is an account inquiry email. Extract the following information:
- account_number: The account number being inquired about
- customer_name: The name of the customer
- inquiry_type: The specific type of inquiry (e.g., balance, statement, etc.)
- date_range: Any date range mentioned (if applicable)
- reference_number: Any reference number mentioned

Email Subject: {subject}

Email Body:
{body}

Provide your answer in JSON format with these fields.
"""

STATEMENT_REQUEST_EXTRACTION_PROMPT = """
This is a statement request email. Extract the following information:
- account_number: The account number for the statement
- customer_name: The name of the customer
- statement_period: The period for the requested statement
- delivery_method: How the statement should be delivered (e.g., email, mail)
- reference_number: Any reference number mentioned

Email Subject: {subject}

Email Body:
{body}

Provide your answer in JSON format with these fields.
"""

# Response generation prompts
EMAIL_RESPONSE_PROMPT = """
Generate a professional response to the following email:

Original Email Subject: {subject}
From: {from_address}
Request Type: {request_type}

Extracted Information:
{extracted_data}

Write a concise, professional response that addresses the request.
Don't include 'Subject:' or email headers in your response, just the body text.
"""

# Prompt template functions
def get_extraction_prompt_for_request_type(request_type: str) -> str:
    """Get the extraction prompt template for a specific request type.
    
    Args:
        request_type: The type of request
        
    Returns:
        Prompt template string
    """
    request_type = request_type.upper()
    
    if request_type == "REIMBURSEMENT":
        return REIMBURSEMENT_EXTRACTION_PROMPT
    elif request_type == "INVOICE_PAYMENT":
        return INVOICE_PAYMENT_EXTRACTION_PROMPT
    elif request_type == "ACCOUNT_INQUIRY":
        return ACCOUNT_INQUIRY_EXTRACTION_PROMPT
    elif request_type == "STATEMENT_REQUEST":
        return STATEMENT_REQUEST_EXTRACTION_PROMPT
    else:
        return ENTITY_EXTRACTION_PROMPT

def get_entity_types_for_request_type(request_type: str) -> List[str]:
    """Get the list of entity types to extract for a specific request type.
    
    Args:
        request_type: The type of request
        
    Returns:
        List of entity types
    """
    request_type = request_type.upper()
    
    common_types = ["date", "amount", "reference_number"]
    
    if request_type == "REIMBURSEMENT":
        return common_types + ["expense_type", "payee", "account_number"]
    elif request_type == "INVOICE_PAYMENT":
        return common_types + ["invoice_number", "vendor", "due_date", "account_number"]
    elif request_type == "ACCOUNT_INQUIRY":
        return common_types + ["account_number", "customer_name", "inquiry_type"]
    elif request_type == "STATEMENT_REQUEST":
        return common_types + ["account_number", "customer_name", "statement_period", "delivery_method"]
    else:
        return common_types + ["person", "organization", "location", "date", "amount", "account_number"]