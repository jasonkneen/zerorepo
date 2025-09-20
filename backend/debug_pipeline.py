#!/usr/bin/env python3
"""
Debug script to test ZeroRepo pipeline stages individually
"""

import asyncio
import sys
import os
sys.path.insert(0, '/app/backend')

from zerorepo.orchestrator import ZeroRepoOrchestrator
from zerorepo.core.models import ProjectConfig
import json

async def debug_pipeline():
    """Debug each stage of the pipeline."""
    
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
        # Stage A: Proposal
        print("=== STAGE A: PROPOSAL ===")
        capability_graph, feature_paths = await orchestrator.run_proposal_stage()
        
        print(f"Features generated: {len(feature_paths)}")
        print(f"Capability nodes: {len(capability_graph.nodes)}")
        print(f"Capability edges: {len(capability_graph.edges)}")
        
        for i, node in enumerate(capability_graph.nodes[:5]):
            print(f"  Node {i}: {node.id} ({node.kind}) - {node.name}")
            
        for i, edge in enumerate(capability_graph.edges[:5]):
            print(f"  Edge {i}: {edge.from_node} -> {edge.to_node} ({edge.type})")
            
        # Stage B: Implementation
        print("\n=== STAGE B: IMPLEMENTATION ===")
        complete_graph, interfaces = await orchestrator.implementation_controller.build_implementation_graph(capability_graph)
        
        print(f"Final nodes: {len(complete_graph.nodes)}")
        print(f"Final edges: {len(complete_graph.edges)}")
        print(f"Interfaces generated: {len(interfaces)}")
        
        # Print all node types
        node_types = {}
        for node in complete_graph.nodes:
            node_types[node.kind] = node_types.get(node.kind, 0) + 1
        print(f"Node types: {node_types}")
        
        # Check interface generation issue
        print("\n=== DEBUGGING INTERFACE GENERATION ===")
        file_nodes = [n for n in complete_graph.nodes if n.kind == "file"]
        print(f"File nodes found: {len(file_nodes)}")
        
        for file_node in file_nodes:
            print(f"File: {file_node.name} ({file_node.path_hint})")
            feature_paths = file_node.meta.get("features", [])
            print(f"  Features assigned: {feature_paths}")
            
            # Check what capabilities are found
            assigned_caps = []
            for node in complete_graph.nodes:
                if node.kind == "capability":
                    node_feature_path = node.meta.get("feature_path")
                    print(f"  Checking capability: {node.name} with feature_path: {node_feature_path}")
                    if node_feature_path in feature_paths:
                        assigned_caps.append(node)
                        print(f"    -> MATCHED!")
            
            print(f"  Capabilities found for {file_node.name}: {len(assigned_caps)}")
            print()
        from zerorepo.rpg.graph_ops import RPGGraphOps
        graph_ops = RPGGraphOps(complete_graph)
        is_valid, errors = graph_ops.validate_dag()
        
        print(f"Graph valid: {is_valid}")
        if errors:
            print("Errors:")
            for error in errors:
                print(f"  - {error}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await orchestrator.cleanup()

if __name__ == "__main__":
    asyncio.run(debug_pipeline())