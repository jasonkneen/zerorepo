#!/usr/bin/env python3
"""
Test the real LLM client with Emergent integration
"""

import asyncio
import sys
import os

import pytest
from dotenv import load_dotenv

sys.path.insert(0, '/app/backend')

from zerorepo.tools.llm_client import LLMClient

pytestmark = pytest.mark.asyncio

load_dotenv()


async def test_real_llm():
    """Test real LLM integration."""

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        pytest.skip('OPENAI_API_KEY not configured')

    llm_client = LLMClient(api_key, 'gpt-4o-mini')
    
    # Test basic text generation
    print("=== TESTING REAL LLM ===")
    response = await llm_client.generate(
        prompt="Generate a simple 'Hello, World!' function in Python.",
        temperature=0.1,
        max_tokens=200
    )
    
    print(f"Success: {response.success}")
    print(f"Content: {response.content}")
    print(f"Error: {response.error}")
    
    # Test JSON generation
    print("\n=== TESTING JSON GENERATION ===")
    json_response = await llm_client.generate_json(
        prompt="""Generate a JSON response with feature paths for a calculator project.

Output (strict JSON):
{"all_selected_feature_paths": ["math/basic/addition", "math/basic/subtraction"]}""",
        temperature=0.1,
        max_tokens=300
    )
    
    print(f"JSON Response: {json_response}")

if __name__ == "__main__":
    asyncio.run(test_real_llm())
