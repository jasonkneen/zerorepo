"""
Implementation-level construction stage - converts capabilities to file structure and interfaces.
Stage B1: File Structure Encoding
Stage B2: Data-Flow & Interface Encoding
"""

import json
import os
from typing import List, Dict, Set, Optional, Tuple
from ..core.models import RPG, RPGNode, RPGEdge, FileSkeleton, Interface, ProjectConfig
from ..tools.llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)


class ImplementationController:
    """
    Controls the implementation-level construction phase.
    
    Stage B1: Maps capability subgraphs to folder/file structure
    Stage B2: Adds data flows and generates interface specifications
    """
    
    def __init__(self, config: ProjectConfig, llm_client: LLMClient):
        self.config = config
        self.llm_client = llm_client
        
    async def build_implementation_graph(self, capability_graph: RPG) -> Tuple[RPG, Dict[str, str]]:
        """
        Main entry point for implementation construction.
        
        Args:
            capability_graph: RPG from proposal stage
            
        Returns:
            Tuple of (complete_rpg_with_files_and_interfaces, interfaces_map)
        """
        logger.info("Starting implementation-level construction")
        
        # Stage B1: File Structure Encoding
        file_augmented_graph = await self._build_file_structure(capability_graph)
        
        # Stage B2: Data-Flow & Interface Encoding  
        complete_graph, interfaces = await self._build_interfaces_and_dataflow(file_augmented_graph)
        
        logger.info(f"Implementation construction complete. Generated {len(interfaces)} interfaces")
        
        return complete_graph, interfaces
        
    async def _build_file_structure(self, capability_graph: RPG) -> RPG:
        """
        Stage B1: Convert capability subtrees into folder/file hierarchy.
        """
        logger.info("Stage B1: Building file structure from capabilities")
        
        # 1. Generate folder skeleton mapping
        folder_skeleton = await self._generate_folder_skeleton(capability_graph)
        
        # 2. Assign features to files
        file_assignments = await self._assign_features_to_files(capability_graph, folder_skeleton)
        
        # 3. Create file and folder nodes
        file_augmented_graph = self._create_file_nodes(capability_graph, folder_skeleton, file_assignments)
        
        logger.info(f"Created file structure with {len(file_assignments)} files")
        
        return file_augmented_graph
        
    async def _build_interfaces_and_dataflow(self, file_graph: RPG) -> Tuple[RPG, Dict[str, str]]:
        """
        Stage B2: Add data flows and generate interface specifications.
        """
        logger.info("Stage B2: Building data flows and interfaces")
        
        # 1. Generate base classes for shared patterns
        base_classes = await self._generate_base_classes(file_graph)
        
        # 2. Generate interfaces for each file
        interfaces = await self._generate_interfaces(file_graph, base_classes)
        
        # 3. Add data flow edges between modules
        complete_graph = await self._add_data_flow_edges(file_graph, interfaces)
        
        # 4. Create function/class nodes from interfaces
        final_graph = self._create_interface_nodes(complete_graph, interfaces)
        
        return final_graph, interfaces
        
    async def _generate_folder_skeleton(self, capability_graph: RPG) -> FileSkeleton:
        """Generate clean folder layout from capability subtrees."""
        
        # Analyze capability subtrees
        capability_nodes = [n for n in capability_graph.nodes if n.kind == "capability"]
        root_capabilities = [n for n in capability_nodes if not capability_graph.get_edges_to(n.id)]
        
        # Build context for LLM
        capabilities_context = []
        for cap in root_capabilities:
            children = capability_graph.get_children(cap.id)
            child_names = [c.name for c in children if c] 
            capabilities_context.append({
                "name": cap.name,
                "children": child_names,
                "feature_path": cap.meta.get("feature_path", "")
            })
            
        prompt = self._build_folder_skeleton_prompt(capabilities_context)
        
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                temperature=0.1,
                max_tokens=800
            )
            
            if not response.success:
                logger.error(f"LLM generation failed: {response.error}")
                return self._create_fallback_skeleton(capability_nodes)
            
            skeleton_data = json.loads(response.content.strip())
            return FileSkeleton(**skeleton_data)
            
        except Exception as e:
            logger.error(f"Error generating folder skeleton: {str(e)}")
            # Fallback: create basic structure
            return self._create_fallback_skeleton(capability_nodes)
        
    def _build_base_classes_prompt(self, common_patterns: List[Dict]) -> str:
        """Build prompt for base classes generation."""
        patterns_text = "\n".join([
            f"- {pattern['name']}: {pattern['pattern']}" 
            for pattern in common_patterns
        ])
        
        return f"""Define minimal global base classes for shared patterns in this {self.config.target_language} project.

Project Goal: {self.config.project_goal}

Common Patterns Identified:
{patterns_text}

Requirements:
- Create 1-3 base classes maximum
- Use proper type hints and abstractions
- Include comprehensive docstrings
- Make classes extensible but focused
- Follow {self.config.target_language} best practices

Output: Complete code with base class definitions."""
            
    async def _assign_features_to_files(self, capability_graph: RPG, skeleton: FileSkeleton) -> Dict[str, List[str]]:
        """Assign leaf capability features to specific files."""
        
        # Get leaf capability nodes (no children)
        leaf_capabilities = []
        for node in capability_graph.nodes:
            if node.kind == "capability" and not node.children:
                leaf_capabilities.append(node)
                
        # Group capabilities by semantic similarity for file assignment
        capability_groups = self._group_capabilities_by_similarity(leaf_capabilities)
        
        # Build assignment prompt
        prompt = self._build_file_assignment_prompt(capability_groups, skeleton)
        
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                temperature=0.1,
                max_tokens=1000
            )
            
            if not response.success:
                logger.error(f"LLM generation failed: {response.error}")
                return self._create_fallback_assignment(leaf_capabilities, skeleton)
            
            assignment_data = json.loads(response.content.strip())
            return assignment_data
            
        except Exception as e:
            logger.error(f"Error in file assignment: {str(e)}")
            # Fallback: simple assignment
            return self._create_fallback_assignment(leaf_capabilities, skeleton)
            
    async def _generate_base_classes(self, file_graph: RPG) -> Dict[str, str]:
        """Generate minimal base classes for shared IO patterns."""
        
        # Analyze nodes for common patterns
        file_nodes = [n for n in file_graph.nodes if n.kind == "file"]
        
        # Look for patterns in capability groupings
        common_patterns = self._identify_common_patterns(file_graph)
        
        if len(common_patterns) < 2:  # Need at least 2 patterns for base classes
            return {}
            
        prompt = self._build_base_classes_prompt(common_patterns)
        
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=1200
            )
            
            if not response.success:
                logger.error(f"LLM generation failed: {response.error}")
                return {}
            
            # Parse response into base class code
            base_classes = self._parse_base_classes_response(response.content)
            return base_classes
            
        except Exception as e:
            logger.error(f"Error generating base classes: {str(e)}")
            return {}
            
    async def _generate_interfaces(self, file_graph: RPG, base_classes: Dict[str, str]) -> Dict[str, str]:
        """Generate interface specifications for each file."""
        
        interfaces = {}
        file_nodes = [n for n in file_graph.nodes if n.kind == "file"]
        
        for file_node in file_nodes:
            # Get capabilities assigned to this file
            assigned_caps = self._get_file_capabilities(file_graph, file_node)
            
            if not assigned_caps:
                continue
                
            prompt = self._build_interfaces_prompt(file_node, assigned_caps, base_classes)
            
            try:
                response = await self.llm_client.generate(
                    prompt=prompt,
                    temperature=0.1,
                    max_tokens=1500
                )
                
                if not response.success:
                    logger.error(f"LLM generation failed: {response.error}")
                    continue
                
                interfaces[file_node.path_hint] = response.content.strip()
                logger.debug(f"Generated interface for {file_node.path_hint}")
                
            except Exception as e:
                logger.error(f"Error generating interface for {file_node.path_hint}: {str(e)}")
                continue
                
        return interfaces
        
    async def _add_data_flow_edges(self, file_graph: RPG, interfaces: Dict[str, str]) -> RPG:
        """Add typed data flow edges between modules based on interfaces."""
        
        # Analyze interfaces to identify data dependencies
        data_flows = self._analyze_data_dependencies(interfaces)
        
        # Create new edges for data flows
        new_edges = []
        for flow in data_flows:
            source_node = self._find_node_by_path(file_graph, flow["source_file"])
            target_node = self._find_node_by_path(file_graph, flow["target_file"])
            
            if source_node and target_node:
                edge = RPGEdge(
                    from_node=source_node.id,
                    to_node=target_node.id,
                    type="data_flow",
                    data_id=flow["data_name"],
                    data_type=flow["data_type"],
                    note=f"Data flow: {flow['data_name']}"
                )
                new_edges.append(edge)
                
        # Add order edges based on dependencies
        order_edges = self._generate_order_edges(file_graph, data_flows)
        
        # Create updated graph
        updated_graph = RPG(
            nodes=file_graph.nodes.copy(),
            edges=file_graph.edges + new_edges + order_edges,
            metadata=file_graph.metadata.copy()
        )
        
        updated_graph.metadata["stage"] = "implementation"
        updated_graph.metadata["data_flows"] = len(new_edges)
        
        return updated_graph
        
    def _create_interface_nodes(self, complete_graph: RPG, interfaces: Dict[str, str]) -> RPG:
        """Create function/class nodes from interface specifications."""
        
        new_nodes = []
        new_edges = []
        
        for file_path, interface_code in interfaces.items():
            file_node = self._find_node_by_path(complete_graph, file_path)
            if not file_node:
                continue
                
            # Parse interface code to extract functions/classes
            interface_specs = self._parse_interface_code(interface_code, file_path)
            
            for spec in interface_specs:
                # Create function/class node
                node = RPGNode(
                    id=f"if-{len(new_nodes)}",
                    name=spec["name"],
                    kind=spec["kind"],
                    path_hint=file_path,
                    signature=spec["signature"],
                    doc=spec["docstring"],
                    meta={
                        "dependencies": spec.get("dependencies", []),
                        "interface_spec": True
                    }
                )
                new_nodes.append(node)
                
                # Add containment edge from file
                file_node.children.append(node.id)
                edge = RPGEdge(
                    from_node=file_node.id,
                    to_node=node.id,
                    type="depends_on",
                    note="file containment"
                )
                new_edges.append(edge)
                
        # Create final graph
        final_graph = RPG(
            nodes=complete_graph.nodes + new_nodes,
            edges=complete_graph.edges + new_edges,
            metadata=complete_graph.metadata.copy()
        )
        
        final_graph.metadata["interfaces"] = len(new_nodes)
        
        return final_graph
        
    # Helper methods
    
    def _create_file_nodes(self, capability_graph: RPG, skeleton: FileSkeleton, assignments: Dict[str, List[str]]) -> RPG:
        """Create file and folder nodes in the graph."""
        
        new_nodes = capability_graph.nodes.copy()
        new_edges = capability_graph.edges.copy()
        
        # Create folder nodes and connect them to relevant capability nodes
        folder_nodes = {}
        for folder_info in skeleton.folders:
            folder_path = folder_info["name"]
            folder_id = f"folder-{len(new_nodes)}"
            
            node = RPGNode(
                id=folder_id,
                name=os.path.basename(folder_path),
                kind="folder",
                path_hint=folder_path,
                doc=f"Folder: {folder_path}",
                meta={"maps": folder_info.get("maps", [])}
            )
            new_nodes.append(node)
            folder_nodes[folder_path] = folder_id
            
            # Connect folder to related capability nodes
            mapped_capabilities = folder_info.get("maps", [])
            for cap_name in mapped_capabilities:
                # Find capability nodes that match this folder
                for cap_node in capability_graph.nodes:
                    if cap_node.kind == "capability" and cap_name.lower() in cap_node.name.lower():
                        new_edges.append(RPGEdge(
                            from_node=cap_node.id,
                            to_node=folder_id,
                            type="depends_on",
                            note=f"capability {cap_node.name} maps to folder {folder_path}"
                        ))
            
        # Create file nodes and connect them to capabilities and folders
        for file_path, feature_paths in assignments.items():
            file_id = f"file-{len(new_nodes)}"
            
            node = RPGNode(
                id=file_id,
                name=os.path.basename(file_path),
                kind="file",
                path_hint=file_path,
                doc=f"Implementation file for: {', '.join(feature_paths)}",
                meta={"features": feature_paths}
            )
            new_nodes.append(node)
            
            # Connect file to folder (folder containment)
            folder_path = os.path.dirname(file_path)
            if folder_path in folder_nodes:
                parent_folder = folder_nodes[folder_path]
                parent_node = next(n for n in new_nodes if n.id == parent_folder)
                parent_node.children.append(file_id)
                
                edge = RPGEdge(
                    from_node=parent_folder,
                    to_node=file_id,
                    type="depends_on",
                    note="folder containment"
                )
                new_edges.append(edge)
            
            # Connect file to capability nodes based on feature paths
            for feature_path in feature_paths:
                for cap_node in capability_graph.nodes:
                    if cap_node.kind == "capability" and cap_node.meta.get("feature_path") == feature_path:
                        new_edges.append(RPGEdge(
                            from_node=cap_node.id,
                            to_node=file_id,
                            type="depends_on",
                            note=f"capability {feature_path} implemented in {file_path}"
                        ))
                
        return RPG(
            nodes=new_nodes,
            edges=new_edges,
            metadata=capability_graph.metadata.copy()
        )
        
    def _build_folder_skeleton_prompt(self, capabilities: List[Dict]) -> str:
        """Build prompt for folder skeleton generation."""
        caps_text = "\n".join([
            f"- {cap['name']}: {', '.join(cap['children'])}" 
            for cap in capabilities
        ])
        
        output_example = """{
  "folders": [
    {"name": "src/algorithms", "maps": ["ML Algorithms"]},
    {"name": "src/data", "maps": ["Data Processing"]}
  ],
  "files": []
}"""

        return f"""Map capability subtrees into a clean Python folder layout.

Project Goal: {self.config.project_goal}
Target Language: {self.config.target_language}

Capability Subtrees:
{caps_text}

Create a folder structure under 'src/' with logical grouping.
Include auxiliary folders (tests, config, data) as needed.
Keep names pythonic and concise.

Output (strict JSON):
{output_example}"""

    def _build_file_assignment_prompt(self, capability_groups: List[List[RPGNode]], skeleton: FileSkeleton) -> str:
        """Build prompt for assigning features to files."""
        
        groups_text = []
        for i, group in enumerate(capability_groups):
            features = [node.meta.get("feature_path", node.name) for node in group]
            groups_text.append(f"Group {i+1}: {', '.join(features)}")
            
        folders_text = "\n".join([f"- {f['name']}" for f in skeleton.folders])
        
        groups_text_joined = "\n".join(groups_text)
        output_example = """{
  "src/algorithms/regression/linear.py": ["ml/algorithms/regression/linear"],
  "src/algorithms/clustering/kmeans.py": ["ml/algorithms/clustering/kmeans"]
}"""

        return f"""Assign capability features to .py files under the designated folders.

Available Folders:
{folders_text}

Capability Groups to Assign:
{groups_text_joined}

Rules:
- Group by semantic similarity
- Create subfolders when >10 files per folder
- Use descriptive filenames
- One file per logical component

Output (strict JSON):
{output_example}"""

    def _build_interfaces_prompt(self, file_node: RPGNode, capabilities: List[RPGNode], base_classes: Dict[str, str]) -> str:
        """Build prompt for interface generation."""
        
        caps_text = "\n".join([
            f"- {cap.name}: {cap.doc}" 
            for cap in capabilities
        ])
        
        base_classes_text = ""
        if base_classes:
            base_code_blocks = []
            for code in base_classes.values():
                base_code_blocks.append(f"```python\n{code}\n```")
            base_classes_text = f"\nAvailable Base Classes:\n" + "\n".join(base_code_blocks)
            
        return f"""Generate interface specifications for this file.

File: {file_node.path_hint}

Capabilities to Implement:
{caps_text}
{base_classes_text}

For each capability, define exactly one interface (function or class).
Provide:
- Proper imports
- Precise signatures with type hints
- Detailed docstrings
- Use 'pass' for method bodies

Output: Complete Python code with interfaces only (no implementations)."""

    # Additional helper methods would be implemented here for:
    # - _group_capabilities_by_similarity
    # - _identify_common_patterns  
    # - _parse_base_classes_response
    # - _analyze_data_dependencies
    # - _parse_interface_code
    # etc.
    
    def _group_capabilities_by_similarity(self, capabilities: List[RPGNode]) -> List[List[RPGNode]]:
        """Group capabilities by semantic similarity for file assignment."""
        # Simple grouping by feature path prefix
        groups = {}
        for cap in capabilities:
            feature_path = cap.meta.get("feature_path", "")
            prefix = "/".join(feature_path.split("/")[:2]) if "/" in feature_path else "misc"
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(cap)
        return list(groups.values())
        
    def _create_fallback_skeleton(self, capability_nodes: List[RPGNode]) -> FileSkeleton:
        """Create basic folder structure as fallback."""
        return FileSkeleton(
            folders=[
                {"name": "src/core", "maps": ["Core"]},
                {"name": "src/algorithms", "maps": ["Algorithms"]}, 
                {"name": "src/utils", "maps": ["Utilities"]},
                {"name": "tests", "maps": ["Tests"]}
            ],
            files=[]
        )
        
    def _create_fallback_assignment(self, capabilities: List[RPGNode], skeleton: FileSkeleton) -> Dict[str, List[str]]:
        """Create simple file assignments as fallback."""
        assignments = {}
        for i, cap in enumerate(capabilities):
            file_path = f"src/core/module_{i}.py"
            feature_path = cap.meta.get("feature_path", cap.name)
            assignments[file_path] = [feature_path]
        return assignments
        
    def _identify_common_patterns(self, file_graph: RPG) -> List[Dict]:
        """Identify common patterns for base class generation."""
        # Simple pattern identification
        return [
            {"name": "BaseEstimator", "pattern": "fit/predict methods"},
            {"name": "BaseProcessor", "pattern": "transform/process methods"}
        ]
        
    def _get_file_capabilities(self, file_graph: RPG, file_node: RPGNode) -> List[RPGNode]:
        """Get capabilities assigned to a specific file."""
        feature_paths = file_node.meta.get("features", [])
        capabilities = []
        
        for node in file_graph.nodes:
            if node.kind == "capability" and node.meta.get("feature_path") in feature_paths:
                capabilities.append(node)
                
        return capabilities
        
    def _find_node_by_path(self, graph: RPG, path: str) -> Optional[RPGNode]:
        """Find node by path hint."""
        for node in graph.nodes:
            if node.path_hint == path:
                return node
        return None
        
    def _analyze_data_dependencies(self, interfaces: Dict[str, str]) -> List[Dict]:
        """Analyze interface code to identify data dependencies."""
        # Simplified data flow analysis
        return []
        
    def _generate_order_edges(self, file_graph: RPG, data_flows: List[Dict]) -> List[RPGEdge]:
        """Generate execution order edges based on data dependencies."""
        return []
        
    def _parse_interface_code(self, interface_code: str, file_path: str) -> List[Dict]:
        """Parse interface code to extract function/class specifications."""
        # Simplified parsing - would use AST in production
        specs = []
        
        lines = interface_code.split('\n')
        current_spec = None
        
        for line in lines:
            if line.strip().startswith(('def ', 'class ')):
                if current_spec:
                    specs.append(current_spec)
                    
                current_spec = {
                    "name": line.split()[1].split('(')[0].replace(':', ''),
                    "kind": "class" if line.strip().startswith('class') else "function",
                    "signature": line.strip(),
                    "docstring": "Interface specification",
                    "dependencies": []
                }
                
        if current_spec:
            specs.append(current_spec)
            
        return specs
        
    def _parse_base_classes_response(self, response_text: str) -> Dict[str, str]:
        """Parse base classes response into code blocks."""
        base_classes = {}
        
        # Simple parsing of code blocks
        if "```python" in response_text:
            # Extract Python code blocks
            parts = response_text.split("```python")
            for i, part in enumerate(parts[1:], 1):
                if "```" in part:
                    code = part.split("```")[0].strip()
                    if "class " in code:
                        # Extract class name
                        for line in code.split('\n'):
                            if line.strip().startswith('class '):
                                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                                base_classes[class_name] = code
                                break
        else:
            # Fallback: treat entire response as code
            if "class " in response_text:
                base_classes["BaseClass"] = response_text
                
        return base_classes