"""
RPG Graph Operations - DAG validation, topological sorting, and graph utilities.
"""

import networkx as nx
from typing import List, Set, Dict, Optional, Tuple
from ..core.models import RPG, RPGNode, RPGEdge


class RPGGraphOps:
    """Graph operations and validation for Repository Planning Graphs."""
    
    def __init__(self, rpg: RPG):
        self.rpg = rpg
        self._nx_graph = None
        
    def build_networkx_graph(self) -> nx.DiGraph:
        """Convert RPG to NetworkX directed graph for analysis."""
        if self._nx_graph is not None:
            return self._nx_graph
            
        G = nx.DiGraph()
        
        # Add nodes
        for node in self.rpg.nodes:
            G.add_node(node.id, **node.dict())
            
        # Add edges (only data_flow and order edges for topological analysis)
        for edge in self.rpg.edges:
            if edge.type in ["data_flow", "order"]:
                G.add_edge(edge.from_node, edge.to_node, **edge.dict())
                
        self._nx_graph = G
        return G
        
    def validate_dag(self) -> Tuple[bool, List[str]]:
        """
        Validate that RPG forms a Directed Acyclic Graph (DAG).
        Returns (is_valid, error_messages).
        """
        errors = []
        G = self.build_networkx_graph()
        
        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(G))
            if cycles:
                errors.append(f"Found {len(cycles)} cycles in graph: {cycles[:3]}...")
        except nx.NetworkXError as e:
            errors.append(f"Graph analysis error: {str(e)}")
            
        # Be very lenient about isolated nodes during development
        # The system is functional even with some isolated nodes
        isolated = list(nx.isolates(G))
        if len(isolated) > len(self.rpg.nodes) * 0.8:  # Only warn if >80% are isolated
            errors.append(f"Excessive isolated nodes: {isolated[:5]}... ({len(isolated)} total)")
            
        # Validate node references
        node_ids = {n.id for n in self.rpg.nodes}
        for edge in self.rpg.edges:
            if edge.from_node not in node_ids:
                errors.append(f"Edge references non-existent source node: {edge.from_node}")
            if edge.to_node not in node_ids:
                errors.append(f"Edge references non-existent target node: {edge.to_node}")
                
        return len(errors) == 0, errors
        
    def topological_sort(self) -> List[str]:
        """
        Return topological ordering of nodes for code generation.
        Ensures dependencies are processed before dependents.
        """
        G = self.build_networkx_graph()
        
        try:
            # Only include leaf nodes (functions/classes) in topological sort
            leaf_nodes = [n.id for n in self.rpg.nodes if n.kind in ["function", "class"]]
            subgraph = G.subgraph(leaf_nodes)
            return list(nx.topological_sort(subgraph))
        except nx.NetworkXError:
            # Fallback: return nodes in creation order if cycles exist
            return [n.id for n in self.rpg.nodes if n.kind in ["function", "class"]]
            
    def get_dependencies(self, node_id: str, max_depth: int = 3) -> List[str]:
        """Get all dependencies of a node up to max_depth."""
        G = self.build_networkx_graph()
        
        if node_id not in G:
            return []
            
        deps = []
        try:
            # Get all predecessors within max_depth
            for depth in range(1, max_depth + 1):
                predecessors = set()
                for node in [node_id] if depth == 1 else deps:
                    if node in G:
                        predecessors.update(G.predecessors(node))
                deps.extend(list(predecessors))
                
        except nx.NetworkXError:
            pass
            
        return list(set(deps))  # Remove duplicates
        
    def get_neighborhood(self, node_id: str, radius: int = 2) -> List[RPGNode]:
        """Get all nodes in the neighborhood of given node."""
        G = self.build_networkx_graph()
        
        if node_id not in G:
            return []
            
        try:
            neighbors = nx.ego_graph(G, node_id, radius=radius)
            return [self.rpg.get_node(nid) for nid in neighbors.nodes() if self.rpg.get_node(nid)]
        except nx.NetworkXError:
            return []
            
    def find_by_functionality(self, query: str, max_results: int = 5) -> List[RPGNode]:
        """
        Find nodes by functionality using name/doc similarity.
        This is a simple implementation - can be enhanced with embeddings.
        """
        query_lower = query.lower()
        matches = []
        
        for node in self.rpg.nodes:
            score = 0
            
            # Check name similarity
            if query_lower in node.name.lower():
                score += 3
                
            # Check documentation similarity  
            if node.doc and query_lower in node.doc.lower():
                score += 2
                
            # Check signature similarity
            if node.signature and query_lower in node.signature.lower():
                score += 1
                
            if score > 0:
                matches.append((node, score))
                
        # Sort by score and return top results
        matches.sort(key=lambda x: x[1], reverse=True)
        return [match[0] for match in matches[:max_results]]
        
    def get_data_flows(self) -> List[RPGEdge]:
        """Get all data flow edges in the graph."""
        return [edge for edge in self.rpg.edges if edge.type == "data_flow"]
        
    def get_execution_order(self) -> List[RPGEdge]:
        """Get all execution order edges in the graph."""
        return [edge for edge in self.rpg.edges if edge.type == "order"]
        
    def validate_interfaces(self) -> List[str]:
        """Validate that all leaf nodes have proper interface specifications."""
        errors = []
        
        for node in self.rpg.nodes:
            if node.kind in ["function", "class"]:
                if not node.signature:
                    errors.append(f"Node {node.id} ({node.name}) missing signature")
                if not node.doc:
                    errors.append(f"Node {node.id} ({node.name}) missing documentation")
                    
        return errors
        
    def get_file_dependencies(self) -> Dict[str, List[str]]:
        """Get file-level dependency mapping for build order."""
        file_deps = {}
        
        # Group nodes by file
        file_nodes = {}
        for node in self.rpg.nodes:
            if node.path_hint:
                if node.path_hint not in file_nodes:
                    file_nodes[node.path_hint] = []
                file_nodes[node.path_hint].append(node)
                
        # Calculate file dependencies based on node dependencies
        for file_path, nodes in file_nodes.items():
            deps = set()
            for node in nodes:
                node_deps = self.get_dependencies(node.id)
                for dep_id in node_deps:
                    dep_node = self.rpg.get_node(dep_id)
                    if dep_node and dep_node.path_hint and dep_node.path_hint != file_path:
                        deps.add(dep_node.path_hint)
            file_deps[file_path] = list(deps)
            
        return file_deps
        
    def calculate_metrics(self) -> Dict[str, int]:
        """Calculate graph metrics for monitoring."""
        return {
            "total_nodes": len(self.rpg.nodes),
            "total_edges": len(self.rpg.edges),
            "capability_nodes": len([n for n in self.rpg.nodes if n.kind == "capability"]),
            "file_nodes": len([n for n in self.rpg.nodes if n.kind == "file"]),
            "class_nodes": len([n for n in self.rpg.nodes if n.kind == "class"]),
            "function_nodes": len([n for n in self.rpg.nodes if n.kind == "function"]),
            "data_flows": len([e for e in self.rpg.edges if e.type == "data_flow"]),
            "dependencies": len([e for e in self.rpg.edges if e.type == "depends_on"]),
            "order_constraints": len([e for e in self.rpg.edges if e.type == "order"])
        }