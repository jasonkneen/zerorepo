#!/usr/bin/env python3
"""
Test LLM client mock responses directly
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


async def test_llm_responses():
    """Test what the LLM client is returning."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        pytest.skip('OPENAI_API_KEY not configured')

    llm_client = LLMClient(api_key, 'gpt-4o-mini')
    
    # Test exploit-style prompt
    exploit_prompt = """You are expanding a repository's feature tree with high-relevance paths.

Project Goal: Generate a simple calculator function

Available High-Relevance Features:
- core/math/addition (score: 0.95)
- core/math/subtraction (score: 0.90)

Rules:
- Select only from the available features above
- Maximize coverage of essential capabilities for the project goal
- Avoid duplicates and generic infrastructure (logging, config)
- Focus on core algorithmic and business logic features

Output (strict JSON):
{"all_selected_feature_paths": ["path1", "path2", "path3"]}"""

    print("=== TESTING EXPLOIT PROMPT ===")
    response = await llm_client.generate(exploit_prompt, temperature=0.1, max_tokens=500)
    print(f"Success: {response.success}")
    print(f"Content: {response.content}")
    print(f"Error: {response.error}")
    
    # Test missing features prompt  
    missing_prompt = """Propose missing, implementable features for this repository.

Project Goal: Generate a simple calculator function

Current Features Summary:
**core**: math operations, basic functions

Provide a 3-5 level hierarchy with concrete algorithmic leaves.
Focus on gaps in the current feature set.

Output (strict JSON):
{"missing_features": {"category": {"subcategory": ["leaf_feature_1", "leaf_feature_2"]}}}"""

    print("\n=== TESTING MISSING FEATURES PROMPT ===")
    response = await llm_client.generate(missing_prompt, temperature=0.4, max_tokens=600)
    print(f"Success: {response.success}")
    print(f"Content: {response.content}")
    print(f"Error: {response.error}")

if __name__ == "__main__":
    asyncio.run(test_llm_responses())
