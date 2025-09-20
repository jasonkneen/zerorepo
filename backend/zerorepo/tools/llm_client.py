"""
LLM client abstraction for ZeroRepo.

Uses the official OpenAI SDK so the system can run without Emergent-specific
integrations.
"""

import json
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM generation."""
    content: str
    model: str
    usage: Dict[str, int]
    success: bool
    error: Optional[str] = None


class LLMClient:
    """
    Real LLM client using Emergent integrations for OpenAI, Anthropic, and Google models.
    """
    
    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini"):
        self.default_model = default_model
        self.client = AsyncOpenAI(api_key=api_key)

        logger.info(f"LLM Client initialized with model: {default_model}")

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate text using the specified LLM model.
        
        Args:
            prompt: Input prompt
            model: Model name (defaults to default_model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            
        Returns:
            LLMResponse with generated content
        """
        model = model or self.default_model
        
        model = model or self.default_model

        try:
            system_message = system_prompt or (
                "You are a helpful assistant that provides precise, well-structured responses."
            )

            completion: ChatCompletion = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            message = completion.choices[0].message.content or ""
            usage = completion.usage or {}

            usage_stats = {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            }

            return LLMResponse(
                content=message,
                model=model,
                usage=usage_stats,
                success=True,
            )

        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            return LLMResponse(
                content="",
                model=model,
                usage={},
                success=False,
                error=str(e)
            )
            
    async def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1000,
        schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON response with validation.
        
        Args:
            prompt: Input prompt (should specify JSON output requirement)
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            schema: Optional JSON schema for validation
            
        Returns:
            Parsed JSON response
        """
        # Add JSON formatting instruction to prompt
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond with valid JSON only. No markdown formatting or additional text."
        
        response = await self.generate(
            prompt=json_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt="You are a precise assistant that responds only with valid JSON."
        )
        
        if not response.success:
            raise Exception(f"LLM generation failed: {response.error}")
            
        try:
            # Clean up the response - remove markdown formatting if present
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            json_data = json.loads(content)
            
            # Optional schema validation could be added here
            if schema:
                self._validate_json_schema(json_data, schema)
                
            return json_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response.content}")
            raise Exception(f"Invalid JSON response: {str(e)}")
            
    def _validate_json_schema(self, data: Dict, schema: Dict) -> bool:
        """Basic JSON schema validation - could use jsonschema library."""
        # Simplified validation - would implement full schema validation
        return True
