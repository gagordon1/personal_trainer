from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol, cast
import openai
from django.conf import settings
from openai.types.chat import ChatCompletionMessageParam
import json

class AIProvider(Protocol):
    """Protocol defining the interface for AI providers."""
    
    def generate_completion(self, messages: List[ChatCompletionMessageParam]) -> Dict[str, Any]:
        """Generate a completion from the AI model.
        
        Args:
            messages: List of chat messages to send to the model
            
        Returns:
            Dict containing the model's response
        """
        ...

class OpenAIProvider:
    """Implementation of AIProvider using OpenAI's API."""
    
    def __init__(self):
        """Initialize the OpenAI client."""
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-turbo-preview"  # Using GPT-4 Turbo for better JSON handling
        
    def generate_completion(self, messages: List[ChatCompletionMessageParam]) -> Dict[str, Any]:
        """Generate a completion from OpenAI's API.
        
        Args:
            messages: List of chat messages to send to the model
            
        Returns:
            Dict containing the model's response
            
        Raises:
            ValueError: If the response is not valid JSON
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Balanced between creativity and consistency
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("OpenAI response content is None")
            
            # Parse the JSON response
            try:
                return json.loads(cast(str, content))
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse OpenAI response as JSON: {e}")
                
        except Exception as e:
            raise ValueError(f"OpenAI API error: {str(e)}")

class AnthropicProvider(AIProvider):
    """Anthropic (Claude) implementation of the AI provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL_NAME
        # Import here to avoid dependency if not using Anthropic
        import anthropic
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate_completion(self, messages: List[Dict[str, str]], max_tokens: int = 500) -> str:
        """Generate a completion using Anthropic's API."""
        # Convert messages to Anthropic format
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return str(response.content[0])

def get_ai_provider(provider: str = "openai", **kwargs) -> AIProvider:
    """Factory function to get the appropriate AI provider."""
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    
    if provider not in providers:
        raise ValueError(f"Unsupported AI provider: {provider}")
    
    return providers[provider](**kwargs) 