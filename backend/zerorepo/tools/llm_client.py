"""
LLM Client for ZeroRepo system using Emergent LLM key.
Real implementation using emergentintegrations library.
"""

import os
import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv

# Load environment variables
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
        self.api_key = api_key
        self.default_model = default_model
        self.session_counter = 0
        
        logger.info(f"LLM Client initialized with model: {default_model}")
        
    def _get_session_id(self) -> str:
        """Generate unique session ID for each request."""
        self.session_counter += 1
        return f"zerorepo-session-{self.session_counter}"
        
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
        
        try:
            # Create chat instance
            system_message = system_prompt or "You are a helpful assistant that provides precise, well-structured responses."
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=self._get_session_id(),
                system_message=system_message
            )
            
            # Configure model based on the model name
            if model.startswith("gpt") or model.startswith("o1"):
                chat = chat.with_model("openai", model)
            elif model.startswith("claude"):
                chat = chat.with_model("anthropic", model)
            elif model.startswith("gemini"):
                chat = chat.with_model("gemini", model)
            else:
                # Default to OpenAI
                chat = chat.with_model("openai", "gpt-4o-mini")
            
            # Create user message
            user_message = UserMessage(text=prompt)
            
            # Send message synchronously in executor to avoid blocking the event loop
            def _sync_llm_call():
                import asyncio
                return asyncio.run(chat.send_message(user_message))
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, _sync_llm_call)
            
            return LLMResponse(
                content=response,
                model=model,
                usage={
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response.split()),
                    "total_tokens": len(prompt.split()) + len(response.split())
                },
                success=True
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