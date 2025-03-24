"""Base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the LLM provider.
        
        Args:
            api_key: API key for the provider
            **kwargs: Additional provider-specific parameters
        """
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.0) -> str:
        """Generate text based on a prompt.
        
        Args:
            prompt: The prompt text
            max_tokens: Maximum number of tokens to generate
            temperature: Creativity temperature (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def extract_entities(self, text: str, entity_types: List[str]) -> List[Dict[str, Any]]:
        """Extract entities from text.
        
        Args:
            text: Text to extract entities from
            entity_types: List of entity types to extract
            
        Returns:
            List of extracted entities with type and value
        """
        pass
    
    @abstractmethod
    def categorize_text(self, text: str, categories: List[str]) -> Dict[str, float]:
        """Categorize text into provided categories.
        
        Args:
            text: Text to categorize
            categories: List of possible categories
            
        Returns:
            Dictionary mapping categories to confidence scores
        """
        pass
    
    @abstractmethod
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in characters
            
        Returns:
            Summarized text
        """
        pass
    
    @abstractmethod
    def extract_structured_data(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from text based on a schema.
        
        Args:
            text: Text to extract data from
            schema: Schema defining the structure of data to extract
            
        Returns:
            Dictionary of extracted structured data
        """
        pass