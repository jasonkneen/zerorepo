"""
Shared test fixtures and configurations for ZeroRepo test suite.
"""

import os
import sys
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Import core models (always available)
from zerorepo.core.models import (
    RPG, RPGNode, RPGEdge, FeaturePath, FileSkeleton,
    Interface, ProjectConfig, GenerationResult
)

# Try to import optional modules with graceful fallback
try:
    from zerorepo.tools.llm_client import LLMClient, LLMResponse
except ImportError:
    LLMClient = None
    LLMResponse = None

try:
    from zerorepo.tools.vector_store import VectorStore
except ImportError:
    VectorStore = None

try:
    from zerorepo.tools.docker_runtime import DockerTestRunner
except ImportError:
    DockerTestRunner = None

try:
    from zerorepo.rpg.graph_ops import RPGGraphOps
except ImportError:
    RPGGraphOps = None


# ============================================================
# Pytest Configuration
# ============================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks as integration tests")
    config.addinivalue_line("markers", "unit: marks as unit tests")


# ============================================================
# Core Model Fixtures
# ============================================================

@pytest.fixture
def sample_rpg_node() -> RPGNode:
    """Create a sample RPG node for testing."""
    return RPGNode(
        id="test-node-001",
        name="TestNode",
        kind="capability",
        path_hint="src/test/module.py",
        signature="def test_function(x: int) -> int:",
        doc="A test function that doubles the input",
        children=["child-001", "child-002"],
        meta={"tags": ["test", "sample"], "owner": "test"}
    )


@pytest.fixture
def sample_function_node() -> RPGNode:
    """Create a sample function node."""
    return RPGNode(
        id="func-node-001",
        name="calculate_sum",
        kind="function",
        path_hint="src/math/operations.py",
        signature="def calculate_sum(a: int, b: int) -> int:",
        doc="Calculates the sum of two integers",
        children=[],
        meta={"feature_path": "math/operations/sum"}
    )


@pytest.fixture
def sample_class_node() -> RPGNode:
    """Create a sample class node."""
    return RPGNode(
        id="class-node-001",
        name="DataProcessor",
        kind="class",
        path_hint="src/data/processor.py",
        signature="class DataProcessor(BaseProcessor):",
        doc="Processes data according to specified rules",
        children=["method-001", "method-002"],
        meta={"feature_path": "data/processing"}
    )


@pytest.fixture
def sample_rpg_edge() -> RPGEdge:
    """Create a sample RPG edge for testing."""
    return RPGEdge(
        from_node="node-001",
        to_node="node-002",
        type="data_flow",
        data_id="training_data",
        data_type="numpy.ndarray",
        note="Data flow from loader to processor"
    )


@pytest.fixture
def sample_feature_path() -> FeaturePath:
    """Create a sample feature path."""
    return FeaturePath(
        path="ml/algorithms/regression/linear",
        score=0.85,
        source="exploit"
    )


@pytest.fixture
def sample_file_skeleton() -> FileSkeleton:
    """Create a sample file skeleton."""
    return FileSkeleton(
        folders=[
            {"name": "src/core", "maps": ["Core"]},
            {"name": "src/algorithms", "maps": ["Algorithms"]},
            {"name": "tests", "maps": ["Tests"]}
        ],
        files=[
            {
                "path": "src/core/base.py",
                "features": ["core/base"],
                "order_after": []
            }
        ]
    )


@pytest.fixture
def sample_interface() -> Interface:
    """Create a sample interface."""
    return Interface(
        file="src/algorithms/linear.py",
        kind="class",
        name="LinearRegressor",
        signature="class LinearRegressor(BaseEstimator):",
        docstring="Linear regression implementation using gradient descent.",
        stubs="class LinearRegressor(BaseEstimator):\n    def fit(self, X, y):\n        pass",
        dependencies=["numpy", "BaseEstimator"]
    )


@pytest.fixture
def sample_project_config() -> ProjectConfig:
    """Create a sample project configuration."""
    return ProjectConfig(
        project_goal="Generate a classical ML toolkit with regression and clustering",
        domain="ml",
        target_language="python",
        test_framework="pytest",
        max_iterations=5,
        max_retries=3,
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        temperature=0.1,
        vector_db_type="faiss",
        embedding_model="all-MiniLM-L6-v2"
    )


@pytest.fixture
def sample_generation_result() -> GenerationResult:
    """Create a sample generation result."""
    return GenerationResult(
        success=True,
        generated_files=["src/core/base.py", "src/algorithms/linear.py"],
        failed_files=[],
        test_results={"passed": 10, "failed": 0},
        errors=[],
        metrics={"total_loc": 250, "generation_time": 45.5}
    )


# ============================================================
# RPG Graph Fixtures
# ============================================================

@pytest.fixture
def simple_rpg() -> RPG:
    """Create a simple RPG for testing."""
    nodes = [
        RPGNode(id="cap-1", name="ML Algorithms", kind="capability",
                meta={"feature_path": "ml/algorithms"}),
        RPGNode(id="cap-2", name="Linear Regression", kind="capability",
                meta={"feature_path": "ml/algorithms/regression/linear"}),
        RPGNode(id="folder-1", name="src", kind="folder", path_hint="src/"),
        RPGNode(id="file-1", name="linear.py", kind="file",
                path_hint="src/algorithms/linear.py",
                meta={"features": ["ml/algorithms/regression/linear"]}),
        RPGNode(id="func-1", name="fit", kind="function",
                path_hint="src/algorithms/linear.py",
                signature="def fit(self, X, y):",
                doc="Fit the linear model")
    ]

    edges = [
        RPGEdge(from_node="cap-1", to_node="cap-2", type="depends_on"),
        RPGEdge(from_node="cap-2", to_node="file-1", type="depends_on"),
        RPGEdge(from_node="file-1", to_node="func-1", type="depends_on"),
        RPGEdge(from_node="folder-1", to_node="file-1", type="order")
    ]

    return RPG(
        nodes=nodes,
        edges=edges,
        metadata={"stage": "test", "project_goal": "Test ML toolkit"}
    )


@pytest.fixture
def complex_rpg() -> RPG:
    """Create a more complex RPG with multiple paths and dependencies."""
    nodes = [
        # Capability nodes
        RPGNode(id="cap-ml", name="Machine Learning", kind="capability",
                meta={"feature_path": "ml"}),
        RPGNode(id="cap-regression", name="Regression", kind="capability",
                meta={"feature_path": "ml/regression"}),
        RPGNode(id="cap-classification", name="Classification", kind="capability",
                meta={"feature_path": "ml/classification"}),
        RPGNode(id="cap-linear", name="Linear Regression", kind="capability",
                meta={"feature_path": "ml/regression/linear"}),
        RPGNode(id="cap-logistic", name="Logistic Regression", kind="capability",
                meta={"feature_path": "ml/classification/logistic"}),

        # Folder nodes
        RPGNode(id="folder-src", name="src", kind="folder", path_hint="src/"),
        RPGNode(id="folder-algo", name="algorithms", kind="folder",
                path_hint="src/algorithms/"),

        # File nodes
        RPGNode(id="file-base", name="base.py", kind="file",
                path_hint="src/algorithms/base.py"),
        RPGNode(id="file-linear", name="linear.py", kind="file",
                path_hint="src/algorithms/linear.py",
                meta={"features": ["ml/regression/linear"]}),
        RPGNode(id="file-logistic", name="logistic.py", kind="file",
                path_hint="src/algorithms/logistic.py",
                meta={"features": ["ml/classification/logistic"]}),

        # Function/class nodes
        RPGNode(id="class-base", name="BaseEstimator", kind="class",
                path_hint="src/algorithms/base.py",
                signature="class BaseEstimator:",
                doc="Base class for all estimators"),
        RPGNode(id="class-linear", name="LinearRegressor", kind="class",
                path_hint="src/algorithms/linear.py",
                signature="class LinearRegressor(BaseEstimator):",
                doc="Linear regression implementation"),
        RPGNode(id="class-logistic", name="LogisticClassifier", kind="class",
                path_hint="src/algorithms/logistic.py",
                signature="class LogisticClassifier(BaseEstimator):",
                doc="Logistic classification implementation"),
    ]

    edges = [
        # Capability hierarchy
        RPGEdge(from_node="cap-ml", to_node="cap-regression", type="depends_on"),
        RPGEdge(from_node="cap-ml", to_node="cap-classification", type="depends_on"),
        RPGEdge(from_node="cap-regression", to_node="cap-linear", type="depends_on"),
        RPGEdge(from_node="cap-classification", to_node="cap-logistic", type="depends_on"),

        # File structure
        RPGEdge(from_node="folder-src", to_node="folder-algo", type="order"),
        RPGEdge(from_node="folder-algo", to_node="file-base", type="order"),
        RPGEdge(from_node="folder-algo", to_node="file-linear", type="order"),
        RPGEdge(from_node="folder-algo", to_node="file-logistic", type="order"),

        # Code dependencies
        RPGEdge(from_node="file-base", to_node="class-base", type="depends_on"),
        RPGEdge(from_node="file-linear", to_node="class-linear", type="depends_on"),
        RPGEdge(from_node="file-logistic", to_node="class-logistic", type="depends_on"),

        # Data flow
        RPGEdge(from_node="class-base", to_node="class-linear", type="data_flow",
                data_id="base_interface", data_type="BaseEstimator"),
        RPGEdge(from_node="class-base", to_node="class-logistic", type="data_flow",
                data_id="base_interface", data_type="BaseEstimator"),
    ]

    return RPG(
        nodes=nodes,
        edges=edges,
        metadata={"stage": "implementation", "project_goal": "Complete ML toolkit"}
    )


@pytest.fixture
def cyclic_rpg() -> RPG:
    """Create an RPG with cycles for testing cycle detection."""
    nodes = [
        RPGNode(id="node-a", name="Node A", kind="capability"),
        RPGNode(id="node-b", name="Node B", kind="capability"),
        RPGNode(id="node-c", name="Node C", kind="capability"),
    ]

    # Create a cycle: A -> B -> C -> A
    edges = [
        RPGEdge(from_node="node-a", to_node="node-b", type="data_flow"),
        RPGEdge(from_node="node-b", to_node="node-c", type="data_flow"),
        RPGEdge(from_node="node-c", to_node="node-a", type="data_flow"),
    ]

    return RPG(nodes=nodes, edges=edges, metadata={})


@pytest.fixture
def empty_rpg() -> RPG:
    """Create an empty RPG for edge case testing."""
    return RPG(nodes=[], edges=[], metadata={})


# ============================================================
# Mock Fixtures
# ============================================================

@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    mock = MagicMock()
    mock.default_model = "gpt-4o-mini"

    # Create a simple mock response object
    class MockLLMResponse:
        def __init__(self):
            self.content = '{"all_selected_feature_paths": ["ml/algorithms/linear"]}'
            self.model = "gpt-4o-mini"
            self.usage = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
            self.success = True
            self.error = None

    async def mock_generate(*args, **kwargs):
        return MockLLMResponse()

    async def mock_generate_json(*args, **kwargs):
        return {"all_selected_feature_paths": ["ml/algorithms/linear"]}

    mock.generate = AsyncMock(side_effect=mock_generate)
    mock.generate_json = AsyncMock(side_effect=mock_generate_json)

    return mock


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    class MockResponse:
        content = "def test_function():\n    return 42"
        model = "gpt-4o-mini"
        usage = {"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70}
        success = True
        error = None
    return MockResponse()


@pytest.fixture
def mock_llm_response_json():
    """Create a mock LLM response with JSON content."""
    class MockResponse:
        content = '{"features": ["feature1", "feature2"], "score": 0.85}'
        model = "gpt-4o-mini"
        usage = {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80}
        success = True
        error = None
    return MockResponse()


@pytest.fixture
def mock_llm_response_error():
    """Create a mock LLM error response."""
    class MockResponse:
        content = ""
        model = "gpt-4o-mini"
        usage = {}
        success = False
        error = "API rate limit exceeded"
    return MockResponse()


@pytest.fixture
def mock_docker_runner():
    """Create a mock Docker test runner."""
    mock = MagicMock(spec=DockerTestRunner)

    async def mock_run_tests(*args, **kwargs):
        return {
            "success": True,
            "output": "===== 5 passed in 0.5s =====",
            "exit_code": 0,
            "error": ""
        }

    async def mock_run_all_tests(*args, **kwargs):
        return {
            "success": True,
            "output": "===== 10 passed in 2.0s =====",
            "exit_code": 0,
            "total_tests": 10,
            "passed_tests": 10,
            "failed_tests": 0
        }

    mock.run_tests = AsyncMock(side_effect=mock_run_tests)
    mock.run_all_tests = AsyncMock(side_effect=mock_run_all_tests)
    mock.cleanup = MagicMock()

    return mock


# ============================================================
# Temporary Directory Fixtures
# ============================================================

@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test output."""
    temp_dir = tempfile.mkdtemp(prefix="zerorepo_test_")
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_project_dir(temp_output_dir):
    """Create a temporary project directory with structure."""
    src_dir = os.path.join(temp_output_dir, "src")
    tests_dir = os.path.join(temp_output_dir, "tests")
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    # Create a simple test file
    test_file = os.path.join(tests_dir, "test_sample.py")
    with open(test_file, "w") as f:
        f.write("def test_sample():\n    assert True\n")

    return temp_output_dir


# ============================================================
# Feature Path Fixtures
# ============================================================

@pytest.fixture
def sample_feature_paths() -> List[FeaturePath]:
    """Create a list of sample feature paths."""
    return [
        FeaturePath(path="ml/algorithms/regression/linear", score=0.9, source="exploit"),
        FeaturePath(path="ml/algorithms/regression/polynomial", score=0.85, source="exploit"),
        FeaturePath(path="ml/algorithms/classification/logistic", score=0.8, source="explore"),
        FeaturePath(path="ml/preprocessing/scaling", score=0.7, source="explore"),
        FeaturePath(path="ml/evaluation/metrics", score=0.75, source="missing"),
        FeaturePath(path="data/loading", score=0.6, source="ontology"),
    ]


@pytest.fixture
def ml_ontology() -> Dict:
    """Create a sample ML ontology."""
    return {
        "ml": {
            "algorithms": {
                "supervised": {
                    "regression": ["linear", "polynomial", "ridge"],
                    "classification": ["logistic", "svm", "decision_tree"]
                },
                "unsupervised": {
                    "clustering": ["kmeans", "hierarchical", "dbscan"]
                }
            },
            "preprocessing": {
                "scaling": ["standard", "minmax", "robust"],
                "encoding": ["onehot", "label"]
            },
            "evaluation": {
                "metrics": ["accuracy", "precision", "recall", "f1"]
            }
        }
    }


# ============================================================
# Interface Fixtures
# ============================================================

@pytest.fixture
def sample_interfaces() -> Dict[str, str]:
    """Create sample interface specifications."""
    return {
        "src/algorithms/linear.py": '''
from typing import List
import numpy as np

class LinearRegressor:
    """Linear regression using gradient descent."""

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LinearRegressor":
        """Fit the model to training data."""
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        pass
''',
        "src/algorithms/base.py": '''
from abc import ABC, abstractmethod

class BaseEstimator(ABC):
    """Base class for all estimators."""

    @abstractmethod
    def fit(self, X, y):
        pass

    @abstractmethod
    def predict(self, X):
        pass
'''
    }


# ============================================================
# Async Event Loop Fixture
# ============================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================
# Environment Fixtures
# ============================================================

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "OPENAI_API_KEY": "test-api-key-12345",
        "EMERGENT_LLM_KEY": "test-emergent-key-12345",
        "MONGO_URL": "",
        "DB_NAME": "zerorepo_test"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


# ============================================================
# Test Data Generators
# ============================================================

def create_test_node(
    node_id: str = "test-node",
    name: str = "TestNode",
    kind: str = "capability",
    **kwargs
) -> RPGNode:
    """Factory function to create test nodes."""
    return RPGNode(
        id=node_id,
        name=name,
        kind=kind,
        **kwargs
    )


def create_test_edge(
    from_node: str = "from-node",
    to_node: str = "to-node",
    edge_type: str = "data_flow",
    **kwargs
) -> RPGEdge:
    """Factory function to create test edges."""
    return RPGEdge(
        from_node=from_node,
        to_node=to_node,
        type=edge_type,
        **kwargs
    )


def create_test_rpg(
    num_nodes: int = 5,
    num_edges: int = 3
) -> RPG:
    """Factory function to create test RPGs with configurable size."""
    nodes = [
        RPGNode(id=f"node-{i}", name=f"Node{i}", kind="capability")
        for i in range(num_nodes)
    ]

    edges = []
    for i in range(min(num_edges, num_nodes - 1)):
        edges.append(RPGEdge(
            from_node=f"node-{i}",
            to_node=f"node-{i+1}",
            type="data_flow"
        ))

    return RPG(nodes=nodes, edges=edges, metadata={})
