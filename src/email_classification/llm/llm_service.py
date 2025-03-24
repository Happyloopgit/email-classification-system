"""LLM service for managing provider interactions."""

import os
import logging
from typing import Dict, Any, List, Optional, Union, Type

from email_classification.llm.llm_provider import LLMProvider
from email_classification.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

class LLMService:
    """Service for managing LLM provider interactions."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one service instance."""
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the LLM service."""
        if self._initialized:
            return
            
        # Get provider type from environment variable or default to OpenAI
        provider_type = os.getenv("LLM_PROVIDER", "openai").lower()
        model = os.getenv("LLM_MODEL")
        api_key = os.getenv("LLM_API_KEY")
        
        # Initialize the appropriate provider
        self.provider = self._get_provider(provider_type, api_key, model)
        logger.info(f"Initialized LLM service with provider: {provider_type}")
        self._initialized = True
    
    def _get_provider(self, provider_type: str, api_key: Optional[str] = None, model: Optional[str] = None) -> LLMProvider:
        """Get provider instance based on type.
        
        Args:
            provider_type: Type of provider ("openai", "anthropic", etc.)
            api_key: Optional API key
            model: Optional model name
            
        Returns:
            LLMProvider instance
        """
        if provider_type == "openai":
            from email_classification.llm.openai_provider import OpenAIProvider
            model = model or "gpt-4"
            return OpenAIProvider(api_key=api_key, model=model)
        elif provider_type == "anthropic":
            try:
                from email_classification.llm.anthropic_provider import AnthropicProvider
                model = model or "claude-3-opus-20240229"
                return AnthropicProvider(api_key=api_key, model=model)
            except ImportError:
                logger.warning("Anthropic provider not available. Falling back to OpenAI.")
                from email_classification.llm.openai_provider import OpenAIProvider
                return OpenAIProvider(api_key=api_key)
        else:
            logger.warning(f"Unknown provider type: {provider_type}. Falling back to OpenAI.")
            return OpenAIProvider(api_key=api_key)
    
    def set_provider(self, provider: LLMProvider) -> None:
        """Set the LLM provider explicitly.
        
        Args:
            provider: LLMProvider instance to use
        """
        self.provider = provider
        logger.info(f"Set LLM provider to: {provider.__class__.__name__}")
    
    def extract_entities_from_email(self, email_content: Dict[str, Any], entity_types: List[str]) -> List[Dict[str, Any]]:
        """Extract entities from email content.
        
        Args:
            email_content: Email content dictionary with subject and body
            entity_types: List of entity types to extract
            
        Returns:
            List of extracted entities
        """
        try:
            # Combine subject and body for analysis
            text = f"Subject: {email_content.get('subject', '')}\n\n{email_content.get('plain_text', '')}"
            
            # Extract entities
            entities = self.provider.extract_entities(text, entity_types)
            logger.info(f"Extracted {len(entities)} entities from email")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities from email: {str(e)}")
            return []
    
    def classify_email(self, email_content: Dict[str, Any], categories: List[str]) -> Dict[str, float]:
        """Classify email content into categories.
        
        Args:
            email_content: Email content dictionary with subject and body
            categories: List of possible categories
            
        Returns:
            Dictionary mapping categories to confidence scores
        """
        try:
            # Combine subject and body for analysis
            text = f"Subject: {email_content.get('subject', '')}\n\n{email_content.get('plain_text', '')}"
            
            # Categorize text
            result = self.provider.categorize_text(text, categories)
            
            logger.info(f"Classified email with categories: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error classifying email: {str(e)}")
            return {cat: 0.0 for cat in categories}
    
    def extract_structured_email_data(self, email_content: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from email.
        
        Args:
            email_content: Email content dictionary with subject and body
            schema: Schema defining the structure of data to extract
            
        Returns:
            Dictionary of extracted structured data
        """
        try:
            # Combine subject and body for analysis
            text = f"Subject: {email_content.get('subject', '')}\n\n{email_content.get('plain_text', '')}"
            
            # Extract structured data
            result = self.provider.extract_structured_data(text, schema)
            
            logger.info(f"Extracted structured data from email: {list(result.keys())}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting structured data from email: {str(e)}")
            return {}
    
    def generate_email_response(self, email_content: Dict[str, Any], extracted_data: Dict[str, Any], request_type: str) -> str:
        """Generate a response to an email.
        
        Args:
            email_content: Original email content
            extracted_data: Extracted data from the email
            request_type: Type of request
            
        Returns:
            Generated response text
        """
        try:
            # Create prompt for response generation
            prompt = f"""Generate a professional email response based on the following information:
            
            Original email subject: {email_content.get('subject', '')}
            From: {email_content.get('from_address', '')}
            Request type: {request_type}
            
            Extracted information:
            {extracted_data}
            
            Write a concise, professional response that addresses the request.
            Don't include 'Subject:' or email headers in your response, just the body text.
            """
            
            # Generate response
            response = self.provider.generate_text(prompt, max_tokens=500, temperature=0.7)
            
            logger.info(f"Generated email response for request type: {request_type}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating email response: {str(e)}")
            return """
            Thank you for your email. We have received your request and will process it shortly.
            
            Regards,
            Customer Service Team
            """