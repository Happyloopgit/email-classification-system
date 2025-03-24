"""OpenAI provider for LLM integration."""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union

from email_classification.llm.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """OpenAI provider for LLM integration."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: str = "gpt-4",
        **kwargs
    ):
        """Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (e.g., "gpt-4", "gpt-3.5-turbo")
            **kwargs: Additional provider-specific parameters
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Provide it directly or set OPENAI_API_KEY environment variable.")
        
        self.model = model
        self.client = None
        
        # Import OpenAI module dynamically to avoid hard dependency
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"Initialized OpenAI provider with model: {model}")
        except ImportError:
            logger.error("Failed to import openai library. Please install it with: pip install openai")
            raise ImportError("OpenAI library is required. Install it with: pip install openai")
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.0) -> str:
        """Generate text based on a prompt using OpenAI.
        
        Args:
            prompt: The prompt text
            max_tokens: Maximum number of tokens to generate
            temperature: Creativity temperature (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers precisely and accurately."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            raise
    
    def extract_entities(self, text: str, entity_types: List[str]) -> List[Dict[str, Any]]:
        """Extract entities from text using OpenAI.
        
        Args:
            text: Text to extract entities from
            entity_types: List of entity types to extract (e.g., ["person", "organization", "date", "amount"])
            
        Returns:
            List of extracted entities with type and value
        """
        try:
            entity_types_str = ", ".join(entity_types)
            prompt = f"""Extract the following entity types from the text: {entity_types_str}.
            
            Format your response as a JSON array of objects with 'type', 'value', and optionally 'metadata' fields.
            For example: [{{'type': 'person', 'value': 'John Smith'}}, {{'type': 'date', 'value': '2023-05-15'}}]
            
            Text to analyze:
            {text}
            
            JSON output:
            """
            
            response = self.generate_text(prompt)
            
            # Extract JSON from response
            try:
                # Try to parse directly first
                entities = json.loads(response)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from text
                import re
                json_match = re.search(r'\[\s*{.*}\s*\]', response, re.DOTALL)
                if json_match:
                    try:
                        entities = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse entities JSON from response: {response}")
                        return []
                else:
                    logger.error(f"No JSON array found in response: {response}")
                    return []
            
            # Validate entities
            valid_entities = []
            for entity in entities:
                if isinstance(entity, dict) and 'type' in entity and 'value' in entity:
                    valid_entities.append(entity)
            
            return valid_entities
            
        except Exception as e:
            logger.error(f"Error extracting entities with OpenAI: {str(e)}")
            return []
    
    def categorize_text(self, text: str, categories: List[str]) -> Dict[str, float]:
        """Categorize text into provided categories using OpenAI.
        
        Args:
            text: Text to categorize
            categories: List of possible categories
            
        Returns:
            Dictionary mapping categories to confidence scores
        """
        try:
            categories_str = ", ".join(categories)
            prompt = f"""Categorize the following text into one of these categories: {categories_str}.
            
            For each category, assign a confidence score between 0.0 and 1.0.
            Format your response as a JSON object where keys are categories and values are confidence scores.
            For example: {{"{categories[0]}": 0.8, "{categories[1]}": 0.2}}
            
            Text to categorize:
            {text}
            
            JSON output:
            """
            
            response = self.generate_text(prompt)
            
            # Extract JSON from response
            try:
                # Try to parse directly first
                categories_dict = json.loads(response)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from text
                import re
                json_match = re.search(r'{.*}', response, re.DOTALL)
                if json_match:
                    try:
                        categories_dict = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse categories JSON from response: {response}")
                        return {cat: 0.0 for cat in categories}
                else:
                    logger.error(f"No JSON object found in response: {response}")
                    return {cat: 0.0 for cat in categories}
            
            # Ensure all categories are present and values are valid
            result = {}
            for cat in categories:
                if cat in categories_dict and isinstance(categories_dict[cat], (int, float)):
                    result[cat] = float(categories_dict[cat])
                else:
                    result[cat] = 0.0
            
            return result
            
        except Exception as e:
            logger.error(f"Error categorizing text with OpenAI: {str(e)}")
            return {cat: 0.0 for cat in categories}
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize text using OpenAI.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in characters
            
        Returns:
            Summarized text
        """
        try:
            prompt = f"""Summarize the following text in a concise way, using no more than {max_length} characters.
            
            Text to summarize:
            {text}
            
            Summary:
            """
            
            summary = self.generate_text(prompt, max_tokens=100, temperature=0.3)
            
            # Truncate to max_length if needed
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing text with OpenAI: {str(e)}")
            return text[:max_length-3] + "..."
    
    def extract_structured_data(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from text based on a schema using OpenAI.
        
        Args:
            text: Text to extract data from
            schema: Schema defining the structure of data to extract
                   Format: {"field_name": {"type": "field_type", "description": "field_description"}}
            
        Returns:
            Dictionary of extracted structured data
        """
        try:
            # Convert schema to string representation
            schema_str = json.dumps(schema, indent=2)
            
            prompt = f"""Extract structured data from the following text according to this schema:
            
            {schema_str}
            
            Format your response as a JSON object containing the extracted data.
            Only include fields specified in the schema. If a field isn't found, set its value to null.
            
            Text to analyze:
            {text}
            
            JSON output:
            """
            
            response = self.generate_text(prompt)
            
            # Extract JSON from response
            try:
                # Try to parse directly first
                data = json.loads(response)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from text
                import re
                json_match = re.search(r'{.*}', response, re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse structured data JSON from response: {response}")
                        return {}
                else:
                    logger.error(f"No JSON object found in response: {response}")
                    return {}
            
            # Validate extracted data
            result = {}
            for field_name in schema:
                if field_name in data:
                    result[field_name] = data[field_name]
                else:
                    result[field_name] = None
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting structured data with OpenAI: {str(e)}")
            return {}