from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import openai
from django.conf import settings
from openai.types.chat import ChatCompletionMessageParam
import json

class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate_completion(self, messages: List[ChatCompletionMessageParam], max_tokens: int = 500) -> str:
        """Generate a completion from the AI model."""
        pass

class OpenAIProvider(AIProvider):
    """OpenAI implementation of the AI provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL_NAME
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_completion(self, messages: List[ChatCompletionMessageParam], max_tokens: int = 500) -> Dict[str, Any]:
        """Generate a completion from the AI model."""
        try:
            # For now, return a mock response
            # In production, this would call the actual OpenAI API
            response = {
                "weekly_plan": [
                    {
                        "day": "Monday",
                        "focus": "Upper Body",
                        "description": "Upper body workout focusing on chest and back",
                        "duration": "45-60 minutes",
                        "intensity": 4,
                        "notes": "Focus on form",
                        "exercises": [
                            {
                                "name": "Push-ups",
                                "sets": 3,
                                "reps": "12-15",
                                "rest": "60 seconds"
                            }
                        ]
                    }
                ],
                "equipment_needed": ["dumbbells", "pull-up bar"],
                "general_guidelines": ["Stay hydrated", "Warm up properly"]
            }
            return response
        except Exception as e:
            raise ValueError(f"Error generating completion: {str(e)}") from e

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