"""
Proposal-level construction stage - builds capabilities graph from feature tree grounding.
Implements explore-exploit strategy with missing feature synthesis.
"""

import json
import random
from typing import List, Dict, Set, Optional, Tuple
from ..core.models import RPG, RPGNode, RPGEdge, FeaturePath, ProjectConfig
from ..tools.llm_client import LLMClient
from ..tools.vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)


class ProposalController:
    """
    Controls the proposal-level construction phase.
    
    Implements Algorithm 1 & 2 from the paper:
    - Feature tree grounding and retrieval
    - Explore-exploit selection balance
    - Missing feature synthesis
    - Iterative refinement with acceptance filters
    """
    
    def __init__(self, config: ProjectConfig, llm_client: LLMClient, vector_store: VectorStore):
        self.config = config
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.selected_features: Set[str] = set()
        self.rejected_features: Set[str] = set()
        
    async def build_capability_graph(self) -> Tuple[RPG, List[FeaturePath]]:
        """
        Main entry point for proposal construction.
        
        Returns:
            Tuple of (capability_graph, selected_feature_paths)
        """
        logger.info(f"Starting proposal construction for: {self.config.project_goal}")
        
        all_feature_paths = []
        
        # Iterative feature selection (Algorithm 2)
        for iteration in range(self.config.max_iterations):
            logger.info(f"Proposal iteration {iteration + 1}/{self.config.max_iterations}")
            
            # 1. Exploit phase - high relevance retrieval
            exploit_paths = await self._exploit_feature_selection(iteration)
            
            # 2. Explore phase - diversity injection  
            explore_paths = await self._explore_feature_selection(iteration)
            
            # 3. Missing features - LLM gap filling
            missing_paths = await self._synthesize_missing_features(iteration)
            
            # 4. Batch acceptance with overlap control
            new_features = self._accept_features(exploit_paths + explore_paths + missing_paths)
            
            if not new_features:
                logger.info(f"No new features accepted in iteration {iteration + 1}, stopping")
                break
                
            all_feature_paths.extend(new_features)
            logger.info(f"Accepted {len(new_features)} new features in iteration {iteration + 1}")
            
        logger.info(f"Proposal construction complete. Total features: {len(all_feature_paths)}")
        
        # Build capability graph from selected features
        capability_graph = self._build_capability_graph(all_feature_paths)
        
        return capability_graph, all_feature_paths
        
    async def _exploit_feature_selection(self, iteration: int) -> List[FeaturePath]:
        """Exploit phase: select high-relevance features using vector retrieval."""
        
        # Build query from project goal and current features
        current_features_context = list(self.selected_features)[-10:]  # Last 10 for context
        query_context = {
            "project_goal": self.config.project_goal,
            "current_repo_paths": current_features_context,
            "iteration": iteration
        }
        
        # Vector retrieval for relevant features
        similar_features = await self.vector_store.search_features(
            query=self.config.project_goal,
            k=20 + iteration * 5,  # Expand search over iterations
            domain_filter=self.config.domain
        )
        
        # Build prompt for LLM
        exploit_prompt = self._build_exploit_prompt(similar_features, query_context)
        
        logger.info(f"Exploit prompt (first 200 chars): {exploit_prompt[:200]}")
        
        try:
            response_json = await self.llm_client.generate_json(
                prompt=exploit_prompt,
                temperature=0.1,  # Low temperature for deterministic selection
                max_tokens=1000
            )
            
            paths = response_json.get("all_selected_feature_paths", [])
            selected_paths = [FeaturePath(path=path, score=0.8, source="exploit") for path in paths]
            
            # Score based on retrieval relevance
            for path in selected_paths:
                matching_feature = next((f for f in similar_features if f.path == path.path), None)
                if matching_feature:
                    path.score = matching_feature.score
                    
            logger.info(f"Exploit phase generated {len(selected_paths)} features")
            return selected_paths
            
        except Exception as e:
            logger.error(f"Error in exploit selection: {str(e)}")
            return []
            
    async def _explore_feature_selection(self, iteration: int) -> List[FeaturePath]:
        """Explore phase: inject diversity with broader feature sampling."""
        
        # Sample from different areas of feature space
        explore_features = await self.vector_store.sample_diverse_features(
            exclude_paths=self.selected_features,
            k=10,
            domain_filter=self.config.domain,
            diversity_weight=0.7
        )
        
        query_context = {
            "project_goal": self.config.project_goal,
            "current_repo_paths": list(self.selected_features),
            "exploration_iteration": iteration
        }
        
        explore_prompt = self._build_explore_prompt(explore_features, query_context)
        
        try:
            response_json = await self.llm_client.generate_json(
                prompt=explore_prompt,
                temperature=0.3,  # Higher temperature for exploration
                max_tokens=800
            )
            
            paths = response_json.get("all_selected_feature_paths", [])
            selected_paths = [FeaturePath(path=path, score=0.6, source="explore") for path in paths]
            
            logger.info(f"Explore phase generated {len(selected_paths)} features")
            return selected_paths
            
        except Exception as e:
            logger.error(f"Error in explore selection: {str(e)}")
            return []
            
    async def _synthesize_missing_features(self, iteration: int) -> List[FeaturePath]:
        """Missing features phase: LLM generates gaps in capability coverage."""
        
        current_features_summary = self._summarize_current_features()
        
        missing_prompt = self._build_missing_prompt(current_features_summary, iteration)
        
        try:
            response_json = await self.llm_client.generate_json(
                prompt=missing_prompt,
                temperature=0.4,  # Creative but focused
                max_tokens=600
            )
            
            missing_features_data = response_json.get("missing_features", {})
            
            if not missing_features_data:
                logger.warning("No missing features in response")
                return []
            
            # Convert to FeaturePath objects
            feature_paths = []
            paths = self._flatten_feature_hierarchy(missing_features_data)
            for path in paths:
                feature_paths.append(FeaturePath(
                    path=path,
                    score=0.5,  # Medium confidence for synthesized features
                    source="missing"
                ))
                
            logger.info(f"Missing phase generated {len(feature_paths)} features")
            return feature_paths
            
        except Exception as e:
            logger.error(f"Error in missing feature synthesis: {str(e)}")
            return []
            
    def _accept_features(self, candidate_paths: List[FeaturePath]) -> List[FeaturePath]:
        """
        Apply acceptance filters to avoid duplicates and maintain quality.
        Implements Algorithm 1 acceptance control.
        """
        accepted = []
        
        for path in candidate_paths:
            # Skip if already selected or rejected
            if path.path in self.selected_features or path.path in self.rejected_features:
                continue
                
            # Skip generic infrastructure features
            if self._is_generic_infrastructure(path.path):
                self.rejected_features.add(path.path)
                continue
                
            # Score-based filtering
            if path.score < 0.2:  # Minimum relevance threshold
                self.rejected_features.add(path.path)
                continue
                
            # Check for excessive similarity to existing features
            if self._is_too_similar_to_existing(path.path):
                self.rejected_features.add(path.path)
                continue
                
            # Accept the feature
            accepted.append(path)
            self.selected_features.add(path.path)
            
        return accepted
        
    def _build_capability_graph(self, feature_paths: List[FeaturePath]) -> RPG:
        """Convert selected feature paths into capability graph with hierarchy."""
        
        nodes = []
        edges = []
        path_to_node = {}
        
        # Build hierarchical nodes from feature paths
        for feature_path in feature_paths:
            path_parts = feature_path.path.split('/')
            
            # Create nodes for each level of hierarchy
            current_path = ""
            parent_node_id = None
            
            for i, part in enumerate(path_parts):
                if current_path:
                    current_path += "/"
                current_path += part
                
                if current_path not in path_to_node:
                    node_id = f"cap-{len(nodes)}"
                    node = RPGNode(
                        id=node_id,
                        name=part.replace('_', ' ').title(),
                        kind="capability",
                        doc=f"Capability: {current_path}",
                        meta={
                            "feature_path": current_path,
                            "source": feature_path.source,
                            "score": feature_path.score
                        }
                    )
                    nodes.append(node)
                    path_to_node[current_path] = node_id
                    
                    # Add containment edge from parent
                    if parent_node_id:
                        parent_node = next(n for n in nodes if n.id == parent_node_id)
                        parent_node.children.append(node_id)
                        
                        edges.append(RPGEdge(
                            from_node=parent_node_id,
                            to_node=node_id,
                            type="depends_on",
                            note="hierarchical containment"
                        ))
                        
                parent_node_id = path_to_node[current_path]
                
        # Add some logical dependency edges between capabilities
        self._add_capability_dependencies(nodes, edges)
        
        rpg = RPG(
            nodes=nodes,
            edges=edges,
            metadata={
                "stage": "proposal",
                "total_features": len(feature_paths),
                "project_goal": self.config.project_goal
            }
        )
        
        return rpg
        
    def _add_capability_dependencies(self, nodes: List[RPGNode], edges: List[RPGEdge]):
        """Add logical dependencies between capability nodes."""
        
        # Simple heuristics for common dependency patterns
        node_map = {n.meta.get("feature_path", ""): n for n in nodes}
        
        dependency_patterns = [
            # Data processing dependencies
            ("data/loading", "data/preprocessing"),
            ("data/preprocessing", "data/validation"),
            
            # ML pipeline dependencies  
            ("ml/data", "ml/algorithms"),
            ("ml/algorithms", "ml/evaluation"),
            ("ml/preprocessing", "ml/algorithms"),
            
            # System dependencies
            ("core/base", "algorithms"),
            ("utils", "algorithms"),
            ("config", "core")
        ]
        
        for source_pattern, target_pattern in dependency_patterns:
            source_nodes = [n for path, n in node_map.items() if source_pattern in path]
            target_nodes = [n for path, n in node_map.items() if target_pattern in path]
            
            for source_node in source_nodes:
                for target_node in target_nodes:
                    if source_node.id != target_node.id:
                        edges.append(RPGEdge(
                            from_node=source_node.id,
                            to_node=target_node.id,
                            type="depends_on",
                            note="logical dependency"
                        ))
                        
    # Helper methods for prompts and parsing
    
    def _build_exploit_prompt(self, similar_features: List[FeaturePath], context: Dict) -> str:
        """Build prompt for exploit feature selection."""
        features_text = "\n".join([f"- {f.path} (score: {f.score:.2f})" for f in similar_features])
        current_features = "\n".join([f"- {path}" for path in context["current_repo_paths"]])
        
        return f"""You are a software repository planning AI. Your job is to select relevant features for a repository.

PROJECT GOAL: {context["project_goal"]}

CURRENT REPOSITORY FEATURES:
{current_features}

AVAILABLE HIGH-RELEVANCE FEATURES:
{features_text}

TASK: Select 3-5 features from the available features that are most essential for the project goal.

RULES:
- Select ONLY from the available features listed above
- Choose features that directly support the project goal
- Avoid generic infrastructure features (logging, config, utils)
- Focus on core business logic and algorithms

RESPONSE FORMAT: You must respond with valid JSON in exactly this format:
{{"all_selected_feature_paths": ["feature1", "feature2", "feature3"]}}

Example response:
{{"all_selected_feature_paths": ["ml/algorithms/regression/linear", "ml/evaluation/metrics"]}}

JSON Response:"""

    def _build_explore_prompt(self, explore_features: List[FeaturePath], context: Dict) -> str:
        """Build prompt for explore feature selection."""
        features_text = "\n".join([f"- {f.path}" for f in explore_features])
        current_features = "\n".join([f"- {path}" for path in context["current_repo_paths"]])
        
        return f"""You are adding diversity to a software repository feature set.

PROJECT GOAL: {context["project_goal"]}

CURRENT FEATURES: 
{current_features}

EXPLORATION CANDIDATES:
{features_text}

TASK: Select 1-2 features that add useful diversity without drifting from the project goal.

RESPONSE FORMAT: You must respond with valid JSON in exactly this format:
{{"all_selected_feature_paths": ["feature1", "feature2"]}}

JSON Response:"""

    def _build_missing_prompt(self, current_summary: str, iteration: int) -> str:
        """Build prompt for missing feature synthesis."""
        return f"""You are identifying missing capabilities for a software repository.

PROJECT GOAL: {self.config.project_goal}

CURRENT FEATURES SUMMARY:
{current_summary}

TASK: Propose missing features that would complete this repository. Provide a 2-3 level hierarchy with specific implementable features.

RESPONSE FORMAT: You must respond with valid JSON in exactly this format:
{{"missing_features": {{"category1": {{"subcategory1": ["feature1", "feature2"]}}, "category2": {{"subcategory2": ["feature3"]}}}}}}

Example:
{{"missing_features": {{"algorithms": {{"sorting": ["quicksort", "mergesort"]}}, "data": {{"validation": ["input_checker"]}}}}}}

JSON Response:"""

    def _parse_feature_response(self, response: str, source: str) -> List[FeaturePath]:
        """Parse LLM response into FeaturePath objects."""
        try:
            # Handle LLMResponse object
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = response
                
            # Clean up response - remove markdown formatting if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Handle case where response might be empty or just whitespace
            if not response_text:
                logger.warning(f"Empty response for {source} feature selection")
                return []
            
            data = json.loads(response_text)
            paths = data.get("all_selected_feature_paths", [])
            
            if not paths:
                logger.warning(f"No feature paths found in {source} response: {data}")
                return []
            
            return [FeaturePath(path=path, score=0.8, source=source) for path in paths]
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {source} feature response: {str(e)}")
            logger.error(f"Response content: {response_text[:500]}...")
            return []
        except Exception as e:
            logger.error(f"Failed to parse {source} feature response: {response}")
            logger.error(f"Parse error: {str(e)}")
            return []
            
    def _parse_missing_features_response(self, response: str) -> List[Dict]:
        """Parse missing features response into hierarchical structure."""
        try:
            # Handle LLMResponse object
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = response
                
            # Clean up response - remove markdown formatting if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Handle case where response might be empty
            if not response_text:
                logger.warning("Empty response for missing features")
                return []
            
            data = json.loads(response_text)
            missing_features = data.get("missing_features", {})
            
            if not missing_features:
                logger.warning(f"No missing features found in response: {data}")
                return []
                
            return [missing_features]
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in missing features response: {str(e)}")
            logger.error(f"Response content: {response_text[:500]}...")
            return []
        except Exception as e:
            logger.error(f"Failed to parse missing features response: {response}")
            logger.error(f"Parse error: {str(e)}")
            return []
            
    def _flatten_feature_hierarchy(self, hierarchy: Dict, prefix: str = "") -> List[str]:
        """Flatten hierarchical feature structure into paths."""
        paths = []
        
        for key, value in hierarchy.items():
            current_path = f"{prefix}/{key}" if prefix else key
            
            if isinstance(value, dict):
                paths.extend(self._flatten_feature_hierarchy(value, current_path))
            elif isinstance(value, list):
                for item in value:
                    paths.append(f"{current_path}/{item}")
            else:
                paths.append(current_path)
                
        return paths
        
    def _summarize_current_features(self) -> str:
        """Summarize current features for missing feature synthesis."""
        if not self.selected_features:
            return "No features selected yet."
            
        # Group features by top-level category
        categories = {}
        for feature_path in self.selected_features:
            parts = feature_path.split('/')
            category = parts[0] if parts else "misc"
            if category not in categories:
                categories[category] = []
            categories[category].append('/'.join(parts[1:]) if len(parts) > 1 else "root")
            
        summary_lines = []
        for category, items in categories.items():
            summary_lines.append(f"**{category}**: {', '.join(items[:5])}")
            
        return "\n".join(summary_lines)
        
    def _is_generic_infrastructure(self, path: str) -> bool:
        """Check if path represents generic infrastructure."""
        generic_patterns = [
            "logging", "config", "utils", "helpers", "common", 
            "base", "abstract", "interface", "setup", "init"
        ]
        
        path_lower = path.lower()
        return any(pattern in path_lower for pattern in generic_patterns)
        
    def _is_too_similar_to_existing(self, new_path: str) -> bool:
        """Check if new path is too similar to existing features."""
        new_parts = set(new_path.split('/'))
        
        for existing_path in self.selected_features:
            existing_parts = set(existing_path.split('/'))
            
            # Calculate Jaccard similarity
            intersection = len(new_parts.intersection(existing_parts))
            union = len(new_parts.union(existing_parts))
            
            if union > 0:
                similarity = intersection / union
                if similarity > 0.8:  # Too similar threshold
                    return True
                    
        return False