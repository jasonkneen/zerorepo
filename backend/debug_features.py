#!/usr/bin/env python3
"""
Debug the feature selection process to see what's being generated vs accepted
"""

import asyncio
import sys
import os
sys.path.insert(0, '/app/backend')

from zerorepo.orchestrator import ZeroRepoOrchestrator
from zerorepo.core.models import ProjectConfig

async def debug_feature_selection():
    """Debug feature selection phases."""
    
    config = ProjectConfig(
        project_goal="Generate a simple calculator function",
        domain="general", 
        max_iterations=2,
        llm_model="gpt-4"
    )
    
    orchestrator = ZeroRepoOrchestrator(
        config,
        emergent_api_key=os.environ.get('EMERGENT_LLM_KEY', 'YOUR_API_KEY')
    )
    
    try:
        # Initialize vector store
        sample_ontology = orchestrator.vector_store.create_sample_ontology()
        orchestrator.vector_store.build_from_ontology(sample_ontology)
        
        # Test each phase individually
        proposal_controller = orchestrator.proposal_controller
        
        print("=== EXPLOIT PHASE ===")
        exploit_paths = await proposal_controller._exploit_feature_selection(0)
        print(f"Exploit features generated: {len(exploit_paths)}")
        for path in exploit_paths:
            print(f"  {path.path} ({path.source})")
            
        print("\n=== EXPLORE PHASE ===")
        explore_paths = await proposal_controller._explore_feature_selection(0)
        print(f"Explore features generated: {len(explore_paths)}")
        for path in explore_paths:
            print(f"  {path.path} ({path.source})")
            
        print("\n=== MISSING PHASE ===")
        missing_paths = await proposal_controller._synthesize_missing_features(0)
        print(f"Missing features generated: {len(missing_paths)}")
        for path in missing_paths:
            print(f"  {path.path} ({path.source})")
            
        print("\n=== ACCEPTANCE FILTER ===")
        all_candidates = exploit_paths + explore_paths + missing_paths
        print(f"Total candidates: {len(all_candidates)}")
        
        accepted = proposal_controller._accept_features(all_candidates)
        print(f"Accepted features: {len(accepted)}")
        for path in accepted:
            print(f"  ✅ {path.path} ({path.source})")
            
        # Check what was rejected
        accepted_paths = {p.path for p in accepted}
        rejected = [p for p in all_candidates if p.path not in accepted_paths]
        print(f"Rejected features: {len(rejected)}")
        for path in rejected:
            print(f"  ❌ {path.path} ({path.source})")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await orchestrator.cleanup()

if __name__ == "__main__":
    asyncio.run(debug_feature_selection())