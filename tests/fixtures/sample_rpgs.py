"""
Sample RPG fixtures for testing.
Provides pre-built RPG structures for various test scenarios.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from zerorepo.core.models import RPG, RPGNode, RPGEdge, FeaturePath


def create_ml_toolkit_rpg() -> RPG:
    """Create a sample ML toolkit RPG."""
    nodes = [
        # Capability nodes
        RPGNode(id="cap-ml", name="Machine Learning", kind="capability",
               meta={"feature_path": "ml"}),
        RPGNode(id="cap-algo", name="Algorithms", kind="capability",
               meta={"feature_path": "ml/algorithms"}),
        RPGNode(id="cap-linear", name="Linear Regression", kind="capability",
               meta={"feature_path": "ml/algorithms/linear"}),
        RPGNode(id="cap-eval", name="Evaluation", kind="capability",
               meta={"feature_path": "ml/evaluation"}),

        # Folder nodes
        RPGNode(id="folder-src", name="src", kind="folder", path_hint="src/"),
        RPGNode(id="folder-algo", name="algorithms", kind="folder", path_hint="src/algorithms/"),
        RPGNode(id="folder-eval", name="evaluation", kind="folder", path_hint="src/evaluation/"),

        # File nodes
        RPGNode(id="file-base", name="base.py", kind="file", path_hint="src/algorithms/base.py",
               meta={"features": ["ml/algorithms"]}),
        RPGNode(id="file-linear", name="linear.py", kind="file", path_hint="src/algorithms/linear.py",
               meta={"features": ["ml/algorithms/linear"]}),
        RPGNode(id="file-metrics", name="metrics.py", kind="file", path_hint="src/evaluation/metrics.py",
               meta={"features": ["ml/evaluation"]}),

        # Class/function nodes
        RPGNode(id="class-base", name="BaseEstimator", kind="class",
               path_hint="src/algorithms/base.py",
               signature="class BaseEstimator:",
               doc="Base class for all estimators"),
        RPGNode(id="class-linear", name="LinearRegressor", kind="class",
               path_hint="src/algorithms/linear.py",
               signature="class LinearRegressor(BaseEstimator):",
               doc="Linear regression implementation"),
        RPGNode(id="func-mse", name="mean_squared_error", kind="function",
               path_hint="src/evaluation/metrics.py",
               signature="def mean_squared_error(y_true, y_pred):",
               doc="Calculate MSE"),
    ]

    edges = [
        # Capability hierarchy
        RPGEdge(from_node="cap-ml", to_node="cap-algo", type="depends_on"),
        RPGEdge(from_node="cap-ml", to_node="cap-eval", type="depends_on"),
        RPGEdge(from_node="cap-algo", to_node="cap-linear", type="depends_on"),

        # Folder structure
        RPGEdge(from_node="folder-src", to_node="folder-algo", type="order"),
        RPGEdge(from_node="folder-src", to_node="folder-eval", type="order"),

        # File containment
        RPGEdge(from_node="folder-algo", to_node="file-base", type="order"),
        RPGEdge(from_node="folder-algo", to_node="file-linear", type="order"),
        RPGEdge(from_node="folder-eval", to_node="file-metrics", type="order"),

        # Class/function containment
        RPGEdge(from_node="file-base", to_node="class-base", type="depends_on"),
        RPGEdge(from_node="file-linear", to_node="class-linear", type="depends_on"),
        RPGEdge(from_node="file-metrics", to_node="func-mse", type="depends_on"),

        # Data flow dependencies
        RPGEdge(from_node="class-base", to_node="class-linear", type="data_flow",
               data_id="base_interface", data_type="BaseEstimator"),
    ]

    return RPG(
        nodes=nodes,
        edges=edges,
        metadata={
            "stage": "implementation",
            "project_goal": "Classical ML Toolkit",
            "domain": "ml"
        }
    )


def create_web_api_rpg() -> RPG:
    """Create a sample web API RPG."""
    nodes = [
        # Capability nodes
        RPGNode(id="cap-web", name="Web API", kind="capability",
               meta={"feature_path": "web"}),
        RPGNode(id="cap-auth", name="Authentication", kind="capability",
               meta={"feature_path": "web/auth"}),
        RPGNode(id="cap-crud", name="CRUD Operations", kind="capability",
               meta={"feature_path": "web/crud"}),

        # Folder nodes
        RPGNode(id="folder-src", name="src", kind="folder", path_hint="src/"),
        RPGNode(id="folder-api", name="api", kind="folder", path_hint="src/api/"),

        # File nodes
        RPGNode(id="file-routes", name="routes.py", kind="file", path_hint="src/api/routes.py"),
        RPGNode(id="file-auth", name="auth.py", kind="file", path_hint="src/api/auth.py"),

        # Function nodes
        RPGNode(id="func-login", name="login", kind="function",
               path_hint="src/api/auth.py",
               signature="async def login(request: LoginRequest):",
               doc="Handle user login"),
        RPGNode(id="func-get-items", name="get_items", kind="function",
               path_hint="src/api/routes.py",
               signature="async def get_items():",
               doc="Get all items"),
    ]

    edges = [
        RPGEdge(from_node="cap-web", to_node="cap-auth", type="depends_on"),
        RPGEdge(from_node="cap-web", to_node="cap-crud", type="depends_on"),
        RPGEdge(from_node="folder-src", to_node="folder-api", type="order"),
        RPGEdge(from_node="folder-api", to_node="file-routes", type="order"),
        RPGEdge(from_node="folder-api", to_node="file-auth", type="order"),
        RPGEdge(from_node="file-auth", to_node="func-login", type="depends_on"),
        RPGEdge(from_node="file-routes", to_node="func-get-items", type="depends_on"),
    ]

    return RPG(
        nodes=nodes,
        edges=edges,
        metadata={
            "stage": "implementation",
            "project_goal": "REST API",
            "domain": "web"
        }
    )


def create_data_pipeline_rpg() -> RPG:
    """Create a sample data pipeline RPG."""
    nodes = [
        # Capability nodes
        RPGNode(id="cap-data", name="Data Pipeline", kind="capability",
               meta={"feature_path": "data"}),
        RPGNode(id="cap-extract", name="Extract", kind="capability",
               meta={"feature_path": "data/extract"}),
        RPGNode(id="cap-transform", name="Transform", kind="capability",
               meta={"feature_path": "data/transform"}),
        RPGNode(id="cap-load", name="Load", kind="capability",
               meta={"feature_path": "data/load"}),

        # Folder nodes
        RPGNode(id="folder-src", name="src", kind="folder", path_hint="src/"),
        RPGNode(id="folder-etl", name="etl", kind="folder", path_hint="src/etl/"),

        # File nodes
        RPGNode(id="file-extract", name="extract.py", kind="file", path_hint="src/etl/extract.py"),
        RPGNode(id="file-transform", name="transform.py", kind="file", path_hint="src/etl/transform.py"),
        RPGNode(id="file-load", name="load.py", kind="file", path_hint="src/etl/load.py"),

        # Class nodes
        RPGNode(id="class-extractor", name="DataExtractor", kind="class",
               path_hint="src/etl/extract.py",
               signature="class DataExtractor:",
               doc="Extract data from sources"),
        RPGNode(id="class-transformer", name="DataTransformer", kind="class",
               path_hint="src/etl/transform.py",
               signature="class DataTransformer:",
               doc="Transform data"),
        RPGNode(id="class-loader", name="DataLoader", kind="class",
               path_hint="src/etl/load.py",
               signature="class DataLoader:",
               doc="Load data to destination"),
    ]

    edges = [
        RPGEdge(from_node="cap-data", to_node="cap-extract", type="depends_on"),
        RPGEdge(from_node="cap-data", to_node="cap-transform", type="depends_on"),
        RPGEdge(from_node="cap-data", to_node="cap-load", type="depends_on"),
        RPGEdge(from_node="cap-extract", to_node="cap-transform", type="order"),
        RPGEdge(from_node="cap-transform", to_node="cap-load", type="order"),
        RPGEdge(from_node="folder-src", to_node="folder-etl", type="order"),
        RPGEdge(from_node="folder-etl", to_node="file-extract", type="order"),
        RPGEdge(from_node="folder-etl", to_node="file-transform", type="order"),
        RPGEdge(from_node="folder-etl", to_node="file-load", type="order"),
        RPGEdge(from_node="file-extract", to_node="class-extractor", type="depends_on"),
        RPGEdge(from_node="file-transform", to_node="class-transformer", type="depends_on"),
        RPGEdge(from_node="file-load", to_node="class-loader", type="depends_on"),
        RPGEdge(from_node="class-extractor", to_node="class-transformer", type="data_flow",
               data_id="extracted_data", data_type="DataFrame"),
        RPGEdge(from_node="class-transformer", to_node="class-loader", type="data_flow",
               data_id="transformed_data", data_type="DataFrame"),
    ]

    return RPG(
        nodes=nodes,
        edges=edges,
        metadata={
            "stage": "implementation",
            "project_goal": "ETL Data Pipeline",
            "domain": "data"
        }
    )


def create_sample_feature_paths() -> list:
    """Create sample feature paths for testing."""
    return [
        FeaturePath(path="ml/algorithms/regression/linear", score=0.95, source="exploit"),
        FeaturePath(path="ml/algorithms/regression/polynomial", score=0.90, source="exploit"),
        FeaturePath(path="ml/algorithms/classification/logistic", score=0.88, source="exploit"),
        FeaturePath(path="ml/algorithms/classification/svm", score=0.85, source="explore"),
        FeaturePath(path="ml/preprocessing/scaling/standard", score=0.80, source="explore"),
        FeaturePath(path="ml/preprocessing/scaling/minmax", score=0.78, source="explore"),
        FeaturePath(path="ml/evaluation/metrics/accuracy", score=0.75, source="missing"),
        FeaturePath(path="ml/evaluation/metrics/precision", score=0.73, source="missing"),
        FeaturePath(path="data/loading/csv", score=0.70, source="ontology"),
        FeaturePath(path="data/loading/json", score=0.68, source="ontology"),
    ]


def create_sample_interfaces() -> dict:
    """Create sample interface specifications."""
    return {
        "src/algorithms/base.py": '''"""Base classes for ML algorithms."""
from abc import ABC, abstractmethod
from typing import Any
import numpy as np

class BaseEstimator(ABC):
    """Base class for all estimators."""

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseEstimator":
        """Fit the model to training data."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions on new data."""
        pass
''',
        "src/algorithms/linear.py": '''"""Linear regression implementation."""
import numpy as np
from .base import BaseEstimator

class LinearRegressor(BaseEstimator):
    """Linear regression using ordinary least squares."""

    def __init__(self):
        self.weights = None
        self.bias = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "LinearRegressor":
        """Fit the linear model."""
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        pass
''',
        "src/evaluation/metrics.py": '''"""Evaluation metrics for ML models."""
import numpy as np

def mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate mean squared error."""
    pass

def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate R-squared score."""
    pass
'''
    }
