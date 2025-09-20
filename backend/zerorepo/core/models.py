"""
Core data models for ZeroRepo - Repository Planning Graph (RPG) system.

These are the authoritative JSON contracts between all system stages,
enforced with pydantic for type safety and validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from uuid import uuid4
from datetime import datetime


class RPGNode(BaseModel):
    """Core RPG Node representing capabilities, folders, files, classes, or functions."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique node identifier")
    name: str = Field(..., description="Capability or artifact name")
    kind: Literal["capability", "folder", "file", "class", "function"] = Field(..., description="Node type")
    path_hint: Optional[str] = Field(None, description="File system path hint, e.g., 'src/algos/linear.py'")
    signature: Optional[str] = Field(None, description="Function/class signature for callable nodes")
    doc: Optional[str] = Field(None, description="Rationale, specification, or docstring")
    children: List[str] = Field(default_factory=list, description="Child node IDs for hierarchy")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "node-123",
                "name": "LinearRegressor",
                "kind": "class", 
                "path_hint": "src/algorithms/regression/linear.py",
                "signature": "class LinearRegressor(BaseEstimator):",
                "doc": "Linear regression implementation with gradient descent",
                "children": ["method-fit", "method-predict"],
                "meta": {"tags": ["ml", "regression"], "owner": "planner"}
            }
        }


class RPGEdge(BaseModel):
    """RPG Edge representing relationships between nodes."""
    
    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Target node ID") 
    type: Literal["data_flow", "depends_on", "order"] = Field(..., description="Edge relationship type")
    data_id: Optional[str] = Field(None, description="Named data flow identifier")
    data_type: Optional[str] = Field(None, description="Data type, e.g., 'numpy.ndarray'")
    note: Optional[str] = Field(None, description="Additional edge description")
    
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "from": "data-loader-123",
                "to": "linear-regressor-456", 
                "type": "data_flow",
                "data_id": "training_data",
                "data_type": "numpy.ndarray",
                "note": "Training dataset flow from loader to algorithm"
            }
        }


class FeaturePath(BaseModel):
    """Feature tree path for grounding and exploration."""
    
    path: str = Field(..., description="Hierarchical feature path like 'ml/evaluation/metrics/silhouette_score'")
    score: float = Field(0.0, description="Relevance score for this feature")
    source: Literal["exploit", "explore", "missing", "ontology"] = Field(..., description="Source of feature selection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "path": "ml/algorithms/regression/linear",
                "score": 0.95,
                "source": "exploit"
            }
        }


class FileSkeleton(BaseModel):
    """File system skeleton mapping from capabilities to folder/file structure."""
    
    folders: List[Dict[str, Any]] = Field(default_factory=list, description="Folder mappings")
    files: List[Dict[str, Any]] = Field(default_factory=list, description="File mappings with dependencies")
    
    class Config:
        json_schema_extra = {
            "example": {
                "folders": [{"name": "src/algos", "maps": ["ML Algorithms"]}],
                "files": [{
                    "path": "src/algos/regression/linear.py",
                    "features": ["ml/algos/regression/linear"],
                    "order_after": ["src/algos/base.py"]
                }]
            }
        }


class Interface(BaseModel):
    """Code interface specification for generated functions/classes."""
    
    file: str = Field(..., description="Target file path")
    kind: Literal["class", "function"] = Field(..., description="Interface type")
    name: str = Field(..., description="Interface name")
    signature: str = Field(..., description="Full signature with types")
    docstring: str = Field(..., description="Comprehensive docstring")
    stubs: str = Field(..., description="Code with pass bodies and typed signatures")
    dependencies: List[str] = Field(default_factory=list, description="Import dependencies")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file": "src/algos/regression/linear.py",
                "kind": "class",
                "name": "LinearRegressor", 
                "signature": "class LinearRegressor(BaseEstimator):",
                "docstring": "Linear regression using gradient descent optimization...",
                "stubs": "class LinearRegressor(BaseEstimator):\n    def fit(self, X, y):\n        pass",
                "dependencies": ["numpy", "BaseEstimator"]
            }
        }


class RPG(BaseModel):
    """Complete Repository Planning Graph."""
    
    nodes: List[RPGNode] = Field(default_factory=list, description="All graph nodes")
    edges: List[RPGEdge] = Field(default_factory=list, description="All graph edges")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Graph metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_node(self, node_id: str) -> Optional[RPGNode]:
        """Get node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
        
    def get_children(self, node_id: str) -> List[RPGNode]:
        """Get all child nodes of a given node."""
        node = self.get_node(node_id)
        if not node:
            return []
        return [self.get_node(child_id) for child_id in node.children if self.get_node(child_id)]
        
    def get_edges_from(self, node_id: str) -> List[RPGEdge]:
        """Get all edges originating from a node."""
        return [edge for edge in self.edges if edge.from_node == node_id]
        
    def get_edges_to(self, node_id: str) -> List[RPGEdge]:
        """Get all edges pointing to a node."""  
        return [edge for edge in self.edges if edge.to_node == node_id]


class ProjectConfig(BaseModel):
    """Project configuration for ZeroRepo generation."""
    
    project_goal: str = Field(..., description="High-level project objective")
    domain: str = Field("general", description="Problem domain (ml, web, data, etc.)")
    target_language: str = Field("python", description="Primary programming language")
    test_framework: str = Field("pytest", description="Testing framework")
    max_iterations: int = Field(30, description="Maximum planning iterations")
    max_retries: int = Field(8, description="Maximum retries per code generation")
    
    # LLM Configuration
    llm_provider: str = Field("emergent", description="LLM provider")
    llm_model: str = Field("gpt-4", description="LLM model name")
    temperature: float = Field(0.1, description="LLM temperature for determinism")
    
    # Vector DB Configuration  
    vector_db_type: str = Field("faiss", description="Vector database type")
    embedding_model: str = Field("all-MiniLM-L6-v2", description="Sentence embedding model")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_goal": "Generate a classical ML toolkit with regression, classification, clustering",
                "domain": "ml",
                "target_language": "python",
                "test_framework": "pytest",
                "max_iterations": 30,
                "llm_provider": "emergent",
                "llm_model": "gpt-4"
            }
        }


class GenerationResult(BaseModel):
    """Result of code generation process."""
    
    success: bool = Field(..., description="Whether generation succeeded")
    generated_files: List[str] = Field(default_factory=list, description="Successfully generated file paths")
    failed_files: List[str] = Field(default_factory=list, description="Failed file paths")
    test_results: Dict[str, Any] = Field(default_factory=dict, description="Test execution results") 
    errors: List[str] = Field(default_factory=list, description="Error messages")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Generation metrics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "generated_files": ["src/algos/linear.py", "tests/test_linear.py"],
                "failed_files": [],
                "test_results": {"passed": 15, "failed": 0},
                "errors": [],
                "metrics": {"total_loc": 450, "generation_time": 120.5}
            }
        }