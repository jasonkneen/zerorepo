"""
Unit tests for ZeroRepo core data models.
Tests Pydantic model validation, serialization, and utility methods.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from zerorepo.core.models import (
    RPGNode, RPGEdge, FeaturePath, FileSkeleton,
    Interface, RPG, ProjectConfig, GenerationResult
)


class TestRPGNode:
    """Tests for RPGNode model."""

    def test_create_minimal_node(self):
        """Test creating node with minimal required fields."""
        node = RPGNode(name="TestNode", kind="capability")
        assert node.name == "TestNode"
        assert node.kind == "capability"
        assert node.id is not None  # Auto-generated
        assert node.children == []
        assert node.meta == {}

    def test_create_full_node(self, sample_rpg_node):
        """Test creating node with all fields."""
        assert sample_rpg_node.id == "test-node-001"
        assert sample_rpg_node.name == "TestNode"
        assert sample_rpg_node.kind == "capability"
        assert sample_rpg_node.path_hint == "src/test/module.py"
        assert sample_rpg_node.signature == "def test_function(x: int) -> int:"
        assert sample_rpg_node.doc == "A test function that doubles the input"
        assert len(sample_rpg_node.children) == 2
        assert sample_rpg_node.meta["tags"] == ["test", "sample"]

    def test_node_kind_validation(self):
        """Test that node kind is restricted to valid values."""
        valid_kinds = ["capability", "folder", "file", "class", "function"]
        for kind in valid_kinds:
            node = RPGNode(name="Test", kind=kind)
            assert node.kind == kind

        with pytest.raises(ValidationError):
            RPGNode(name="Test", kind="invalid_kind")

    def test_node_serialization(self, sample_rpg_node):
        """Test node serialization to dict."""
        node_dict = sample_rpg_node.model_dump()
        assert node_dict["id"] == "test-node-001"
        assert node_dict["name"] == "TestNode"
        assert node_dict["kind"] == "capability"

    def test_node_json_serialization(self, sample_rpg_node):
        """Test node JSON serialization."""
        json_str = sample_rpg_node.model_dump_json()
        assert "test-node-001" in json_str
        assert "TestNode" in json_str

    def test_node_from_dict(self):
        """Test creating node from dictionary."""
        data = {
            "id": "node-123",
            "name": "FromDict",
            "kind": "file",
            "path_hint": "src/test.py"
        }
        node = RPGNode(**data)
        assert node.id == "node-123"
        assert node.name == "FromDict"

    @pytest.mark.parametrize("kind", ["capability", "folder", "file", "class", "function"])
    def test_all_node_kinds(self, kind):
        """Test creation of all valid node kinds."""
        node = RPGNode(name=f"Test{kind}", kind=kind)
        assert node.kind == kind

    def test_node_with_empty_children(self):
        """Test node with explicitly empty children list."""
        node = RPGNode(name="NoChildren", kind="function", children=[])
        assert node.children == []

    def test_node_meta_flexibility(self):
        """Test that meta field accepts arbitrary data."""
        meta = {
            "custom_key": "custom_value",
            "nested": {"a": 1, "b": [1, 2, 3]},
            "list_field": ["x", "y", "z"]
        }
        node = RPGNode(name="MetaTest", kind="capability", meta=meta)
        assert node.meta["custom_key"] == "custom_value"
        assert node.meta["nested"]["a"] == 1


class TestRPGEdge:
    """Tests for RPGEdge model."""

    def test_create_minimal_edge(self):
        """Test creating edge with minimal fields."""
        edge = RPGEdge(from_node="node-1", to_node="node-2", type="data_flow")
        assert edge.from_node == "node-1"
        assert edge.to_node == "node-2"
        assert edge.type == "data_flow"

    def test_create_full_edge(self, sample_rpg_edge):
        """Test creating edge with all fields."""
        assert sample_rpg_edge.from_node == "node-001"
        assert sample_rpg_edge.to_node == "node-002"
        assert sample_rpg_edge.type == "data_flow"
        assert sample_rpg_edge.data_id == "training_data"
        assert sample_rpg_edge.data_type == "numpy.ndarray"
        assert sample_rpg_edge.note == "Data flow from loader to processor"

    def test_edge_type_validation(self):
        """Test that edge type is restricted to valid values."""
        valid_types = ["data_flow", "depends_on", "order"]
        for edge_type in valid_types:
            edge = RPGEdge(from_node="a", to_node="b", type=edge_type)
            assert edge.type == edge_type

        with pytest.raises(ValidationError):
            RPGEdge(from_node="a", to_node="b", type="invalid_type")

    def test_edge_serialization(self, sample_rpg_edge):
        """Test edge serialization."""
        edge_dict = sample_rpg_edge.model_dump(by_alias=True)
        # Note: 'from' and 'to' are aliases
        assert edge_dict["from"] == "node-001"
        assert edge_dict["to"] == "node-002"

    def test_edge_alias_handling(self):
        """Test edge field aliases (from/to vs from_node/to_node)."""
        # Create using alias in input
        edge_data = {
            "from": "source",
            "to": "target",
            "type": "depends_on"
        }
        edge = RPGEdge(**edge_data)
        assert edge.from_node == "source"
        assert edge.to_node == "target"

    @pytest.mark.parametrize("edge_type", ["data_flow", "depends_on", "order"])
    def test_all_edge_types(self, edge_type):
        """Test creation of all valid edge types."""
        edge = RPGEdge(from_node="a", to_node="b", type=edge_type)
        assert edge.type == edge_type


class TestFeaturePath:
    """Tests for FeaturePath model."""

    def test_create_feature_path(self, sample_feature_path):
        """Test creating feature path."""
        assert sample_feature_path.path == "ml/algorithms/regression/linear"
        assert sample_feature_path.score == 0.85
        assert sample_feature_path.source == "exploit"

    def test_feature_path_default_score(self):
        """Test default score value."""
        fp = FeaturePath(path="test/path", source="ontology")
        assert fp.score == 0.0

    def test_feature_path_source_validation(self):
        """Test source field validation."""
        valid_sources = ["exploit", "explore", "missing", "ontology"]
        for source in valid_sources:
            fp = FeaturePath(path="test", source=source)
            assert fp.source == source

        with pytest.raises(ValidationError):
            FeaturePath(path="test", source="invalid_source")

    def test_feature_path_serialization(self, sample_feature_path):
        """Test feature path serialization."""
        fp_dict = sample_feature_path.model_dump()
        assert fp_dict["path"] == "ml/algorithms/regression/linear"
        assert fp_dict["score"] == 0.85
        assert fp_dict["source"] == "exploit"

    @pytest.mark.parametrize("score", [0.0, 0.5, 1.0, -0.5, 1.5])
    def test_feature_path_score_values(self, score):
        """Test various score values."""
        fp = FeaturePath(path="test", score=score, source="exploit")
        assert fp.score == score


class TestFileSkeleton:
    """Tests for FileSkeleton model."""

    def test_create_file_skeleton(self, sample_file_skeleton):
        """Test creating file skeleton."""
        assert len(sample_file_skeleton.folders) == 3
        assert len(sample_file_skeleton.files) == 1

    def test_empty_file_skeleton(self):
        """Test creating empty file skeleton."""
        skeleton = FileSkeleton()
        assert skeleton.folders == []
        assert skeleton.files == []

    def test_file_skeleton_serialization(self, sample_file_skeleton):
        """Test file skeleton serialization."""
        skeleton_dict = sample_file_skeleton.model_dump()
        assert "folders" in skeleton_dict
        assert "files" in skeleton_dict

    def test_file_skeleton_with_complex_data(self):
        """Test file skeleton with complex folder/file data."""
        skeleton = FileSkeleton(
            folders=[
                {"name": "src/core", "maps": ["Core"], "extra": "data"},
                {"name": "src/utils", "maps": ["Utils"]}
            ],
            files=[
                {"path": "src/main.py", "features": ["main"], "order_after": []},
                {"path": "src/config.py", "features": ["config"], "order_after": ["src/main.py"]}
            ]
        )
        assert len(skeleton.folders) == 2
        assert len(skeleton.files) == 2


class TestInterface:
    """Tests for Interface model."""

    def test_create_interface(self, sample_interface):
        """Test creating interface."""
        assert sample_interface.file == "src/algorithms/linear.py"
        assert sample_interface.kind == "class"
        assert sample_interface.name == "LinearRegressor"
        assert "BaseEstimator" in sample_interface.signature

    def test_interface_kind_validation(self):
        """Test interface kind validation."""
        # Valid kinds
        for kind in ["class", "function"]:
            interface = Interface(
                file="test.py",
                kind=kind,
                name="Test",
                signature="def test():",
                docstring="Test",
                stubs="pass"
            )
            assert interface.kind == kind

        with pytest.raises(ValidationError):
            Interface(
                file="test.py",
                kind="invalid",
                name="Test",
                signature="def test():",
                docstring="Test",
                stubs="pass"
            )

    def test_interface_serialization(self, sample_interface):
        """Test interface serialization."""
        interface_dict = sample_interface.model_dump()
        assert interface_dict["file"] == "src/algorithms/linear.py"
        assert interface_dict["name"] == "LinearRegressor"


class TestRPG:
    """Tests for RPG model."""

    def test_create_rpg(self, simple_rpg):
        """Test creating RPG."""
        assert len(simple_rpg.nodes) == 5
        assert len(simple_rpg.edges) == 4
        assert simple_rpg.metadata["stage"] == "test"

    def test_empty_rpg(self, empty_rpg):
        """Test empty RPG."""
        assert empty_rpg.nodes == []
        assert empty_rpg.edges == []
        assert empty_rpg.metadata == {}

    def test_rpg_get_node(self, simple_rpg):
        """Test get_node method."""
        node = simple_rpg.get_node("cap-1")
        assert node is not None
        assert node.name == "ML Algorithms"

        # Non-existent node
        assert simple_rpg.get_node("non-existent") is None

    def test_rpg_get_children(self, complex_rpg):
        """Test get_children method."""
        # First add children to a node
        parent = complex_rpg.get_node("cap-ml")
        if parent:
            parent.children = ["cap-regression", "cap-classification"]

        children = complex_rpg.get_children("cap-ml")
        assert len(children) == 2

    def test_rpg_get_edges_from(self, simple_rpg):
        """Test get_edges_from method."""
        edges = simple_rpg.get_edges_from("cap-1")
        assert len(edges) == 1
        assert edges[0].to_node == "cap-2"

    def test_rpg_get_edges_to(self, simple_rpg):
        """Test get_edges_to method."""
        edges = simple_rpg.get_edges_to("cap-2")
        assert len(edges) == 1
        assert edges[0].from_node == "cap-1"

    def test_rpg_created_at_default(self):
        """Test that created_at is auto-populated."""
        rpg = RPG(nodes=[], edges=[])
        assert rpg.created_at is not None
        assert isinstance(rpg.created_at, datetime)

    def test_rpg_serialization(self, simple_rpg):
        """Test RPG serialization."""
        rpg_dict = simple_rpg.model_dump()
        assert "nodes" in rpg_dict
        assert "edges" in rpg_dict
        assert "metadata" in rpg_dict
        assert "created_at" in rpg_dict


class TestProjectConfig:
    """Tests for ProjectConfig model."""

    def test_create_config(self, sample_project_config):
        """Test creating project config."""
        assert sample_project_config.project_goal == "Generate a classical ML toolkit with regression and clustering"
        assert sample_project_config.domain == "ml"
        assert sample_project_config.target_language == "python"
        assert sample_project_config.test_framework == "pytest"

    def test_config_defaults(self):
        """Test default config values."""
        config = ProjectConfig(project_goal="Test project")
        assert config.domain == "general"
        assert config.target_language == "python"
        assert config.test_framework == "pytest"
        assert config.max_iterations == 30
        assert config.max_retries == 8
        assert config.temperature == 0.1

    def test_config_llm_settings(self, sample_project_config):
        """Test LLM configuration settings."""
        assert sample_project_config.llm_provider == "openai"
        assert sample_project_config.llm_model == "gpt-4o-mini"
        assert sample_project_config.temperature == 0.1

    def test_config_vector_db_settings(self, sample_project_config):
        """Test vector DB configuration."""
        assert sample_project_config.vector_db_type == "faiss"
        assert sample_project_config.embedding_model == "all-MiniLM-L6-v2"

    def test_config_serialization(self, sample_project_config):
        """Test config serialization."""
        config_dict = sample_project_config.model_dump()
        assert config_dict["project_goal"] == "Generate a classical ML toolkit with regression and clustering"
        assert config_dict["llm_model"] == "gpt-4o-mini"


class TestGenerationResult:
    """Tests for GenerationResult model."""

    def test_create_success_result(self, sample_generation_result):
        """Test creating successful generation result."""
        assert sample_generation_result.success is True
        assert len(sample_generation_result.generated_files) == 2
        assert len(sample_generation_result.failed_files) == 0
        assert sample_generation_result.test_results["passed"] == 10

    def test_create_failure_result(self):
        """Test creating failed generation result."""
        result = GenerationResult(
            success=False,
            errors=["File generation failed", "Test execution error"],
            metrics={"failed_at": "code_generation"}
        )
        assert result.success is False
        assert len(result.errors) == 2
        assert result.generated_files == []

    def test_result_defaults(self):
        """Test result default values."""
        result = GenerationResult(success=True)
        assert result.generated_files == []
        assert result.failed_files == []
        assert result.test_results == {}
        assert result.errors == []
        assert result.metrics == {}

    def test_result_with_metrics(self, sample_generation_result):
        """Test result with metrics."""
        assert sample_generation_result.metrics["total_loc"] == 250
        assert sample_generation_result.metrics["generation_time"] == 45.5

    def test_result_serialization(self, sample_generation_result):
        """Test result serialization."""
        result_dict = sample_generation_result.model_dump()
        assert result_dict["success"] is True
        assert "generated_files" in result_dict
        assert "metrics" in result_dict


class TestModelInteroperability:
    """Tests for model interoperability and complex scenarios."""

    def test_rpg_with_all_node_types(self):
        """Test RPG containing all node types."""
        nodes = [
            RPGNode(id="cap", name="Capability", kind="capability"),
            RPGNode(id="folder", name="src", kind="folder"),
            RPGNode(id="file", name="main.py", kind="file"),
            RPGNode(id="class", name="MyClass", kind="class"),
            RPGNode(id="func", name="my_function", kind="function"),
        ]
        edges = [
            RPGEdge(from_node="cap", to_node="folder", type="depends_on"),
            RPGEdge(from_node="folder", to_node="file", type="order"),
            RPGEdge(from_node="file", to_node="class", type="depends_on"),
            RPGEdge(from_node="class", to_node="func", type="data_flow"),
        ]
        rpg = RPG(nodes=nodes, edges=edges)

        assert len(rpg.nodes) == 5
        assert len(rpg.edges) == 4

    def test_config_to_rpg_metadata(self, sample_project_config):
        """Test using config data in RPG metadata."""
        rpg = RPG(
            nodes=[],
            edges=[],
            metadata={
                "project_goal": sample_project_config.project_goal,
                "domain": sample_project_config.domain,
                "llm_model": sample_project_config.llm_model
            }
        )
        assert rpg.metadata["project_goal"] == sample_project_config.project_goal

    def test_full_workflow_models(self, sample_project_config, simple_rpg, sample_generation_result):
        """Test models work together in typical workflow."""
        # Simulate workflow: config -> RPG -> result
        rpg_metadata = {
            "project_goal": sample_project_config.project_goal,
            "stage": "completed"
        }
        simple_rpg.metadata.update(rpg_metadata)

        # Result references RPG data
        result = GenerationResult(
            success=True,
            generated_files=[n.path_hint for n in simple_rpg.nodes if n.path_hint],
            metrics={"nodes_processed": len(simple_rpg.nodes)}
        )

        assert result.success
        assert result.metrics["nodes_processed"] == len(simple_rpg.nodes)
