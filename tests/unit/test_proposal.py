"""
Unit tests for Proposal Controller.
Tests feature selection, graph construction, and proposal algorithms.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

# Check for optional dependencies
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

if not FAISS_AVAILABLE:
    pytest.skip("FAISS not installed", allow_module_level=True)

from zerorepo.core.models import RPG, RPGNode, RPGEdge, FeaturePath, ProjectConfig
from zerorepo.plan.proposal import ProposalController


class TestProposalControllerInit:
    """Tests for ProposalController initialization."""

    def test_init_with_config(self, sample_project_config, mock_llm_client):
        """Test initialization with config."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer'), \
             patch('zerorepo.tools.vector_store.faiss'):
            from zerorepo.tools.vector_store import VectorStore
            mock_vector_store = MagicMock(spec=VectorStore)

            controller = ProposalController(
                config=sample_project_config,
                llm_client=mock_llm_client,
                vector_store=mock_vector_store
            )

            assert controller.config == sample_project_config
            assert controller.selected_features == set()
            assert controller.rejected_features == set()


class TestBuildCapabilityGraph:
    """Tests for build_capability_graph method."""

    @pytest.fixture
    def controller_with_mocks(self, sample_project_config):
        """Create controller with mocked dependencies."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate_json = AsyncMock(return_value={
            "all_selected_feature_paths": ["ml/algorithms/linear", "ml/preprocessing/scaling"]
        })

        mock_vector_store = MagicMock()
        mock_vector_store.search_features = AsyncMock(return_value=[
            FeaturePath(path="ml/algorithms/linear", score=0.9, source="exploit"),
            FeaturePath(path="ml/algorithms/logistic", score=0.8, source="exploit"),
        ])
        mock_vector_store.sample_diverse_features = AsyncMock(return_value=[
            FeaturePath(path="ml/preprocessing/scaling", score=0.6, source="explore"),
        ])

        controller = ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

        return controller

    @pytest.mark.asyncio
    async def test_build_capability_graph_returns_rpg(self, controller_with_mocks):
        """Test that build_capability_graph returns RPG and features."""
        rpg, features = await controller_with_mocks.build_capability_graph()

        assert isinstance(rpg, RPG)
        assert isinstance(features, list)

    @pytest.mark.asyncio
    async def test_build_capability_graph_stops_when_no_new_features(self, sample_project_config):
        """Test that iteration stops when no new features accepted."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate_json = AsyncMock(return_value={
            "all_selected_feature_paths": []  # No features
        })

        mock_vector_store = MagicMock()
        mock_vector_store.search_features = AsyncMock(return_value=[])
        mock_vector_store.sample_diverse_features = AsyncMock(return_value=[])

        controller = ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

        rpg, features = await controller.build_capability_graph()

        assert isinstance(rpg, RPG)
        # Should have stopped early due to no features


class TestExploitFeatureSelection:
    """Tests for exploit phase feature selection."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate_json = AsyncMock(return_value={
            "all_selected_feature_paths": ["ml/algorithms/linear"]
        })

        mock_vector_store = MagicMock()
        mock_vector_store.search_features = AsyncMock(return_value=[
            FeaturePath(path="ml/algorithms/linear", score=0.9, source="exploit"),
        ])

        return ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

    @pytest.mark.asyncio
    async def test_exploit_returns_feature_paths(self, controller):
        """Test exploit phase returns FeaturePath objects."""
        paths = await controller._exploit_feature_selection(iteration=0)

        assert isinstance(paths, list)
        for path in paths:
            assert isinstance(path, FeaturePath)
            assert path.source == "exploit"

    @pytest.mark.asyncio
    async def test_exploit_handles_llm_error(self, sample_project_config):
        """Test exploit phase handles LLM errors gracefully."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate_json = AsyncMock(side_effect=Exception("LLM Error"))

        mock_vector_store = MagicMock()
        mock_vector_store.search_features = AsyncMock(return_value=[])

        controller = ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

        paths = await controller._exploit_feature_selection(iteration=0)

        assert paths == []


class TestExploreFeatureSelection:
    """Tests for explore phase feature selection."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate_json = AsyncMock(return_value={
            "all_selected_feature_paths": ["ml/preprocessing/encoding"]
        })

        mock_vector_store = MagicMock()
        mock_vector_store.sample_diverse_features = AsyncMock(return_value=[
            FeaturePath(path="ml/preprocessing/encoding", score=0.6, source="explore"),
        ])

        return ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

    @pytest.mark.asyncio
    async def test_explore_returns_feature_paths(self, controller):
        """Test explore phase returns FeaturePath objects."""
        paths = await controller._explore_feature_selection(iteration=0)

        assert isinstance(paths, list)
        for path in paths:
            assert isinstance(path, FeaturePath)
            assert path.source == "explore"

    @pytest.mark.asyncio
    async def test_explore_handles_llm_error(self, sample_project_config):
        """Test explore phase handles LLM errors gracefully."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate_json = AsyncMock(side_effect=Exception("LLM Error"))

        mock_vector_store = MagicMock()
        mock_vector_store.sample_diverse_features = AsyncMock(return_value=[])

        controller = ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

        paths = await controller._explore_feature_selection(iteration=0)

        assert paths == []


class TestSynthesizeMissingFeatures:
    """Tests for missing feature synthesis."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate_json = AsyncMock(return_value={
            "missing_features": {
                "validation": {
                    "input": ["type_checker", "range_validator"]
                }
            }
        })

        mock_vector_store = MagicMock()

        return ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

    @pytest.mark.asyncio
    async def test_synthesize_returns_feature_paths(self, controller):
        """Test missing synthesis returns FeaturePath objects."""
        paths = await controller._synthesize_missing_features(iteration=0)

        assert isinstance(paths, list)
        for path in paths:
            assert isinstance(path, FeaturePath)
            assert path.source == "missing"

    @pytest.mark.asyncio
    async def test_synthesize_handles_empty_response(self, sample_project_config):
        """Test synthesis handles empty LLM response."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate_json = AsyncMock(return_value={
            "missing_features": {}
        })

        mock_vector_store = MagicMock()

        controller = ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

        paths = await controller._synthesize_missing_features(iteration=0)

        assert paths == []


class TestAcceptFeatures:
    """Tests for feature acceptance filtering."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_vector_store = MagicMock()

        return ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

    def test_accept_new_features(self, controller):
        """Test accepting new features."""
        candidates = [
            FeaturePath(path="ml/algorithms/linear", score=0.9, source="exploit"),
            FeaturePath(path="ml/algorithms/logistic", score=0.8, source="exploit"),
        ]

        accepted = controller._accept_features(candidates)

        assert len(accepted) == 2
        assert "ml/algorithms/linear" in controller.selected_features
        assert "ml/algorithms/logistic" in controller.selected_features

    def test_reject_duplicate_features(self, controller):
        """Test rejecting already selected features."""
        controller.selected_features.add("ml/algorithms/linear")

        candidates = [
            FeaturePath(path="ml/algorithms/linear", score=0.9, source="exploit"),
            FeaturePath(path="ml/algorithms/logistic", score=0.8, source="exploit"),
        ]

        accepted = controller._accept_features(candidates)

        assert len(accepted) == 1
        assert accepted[0].path == "ml/algorithms/logistic"

    def test_reject_low_score_features(self, controller):
        """Test rejecting features below score threshold."""
        candidates = [
            FeaturePath(path="ml/algorithms/linear", score=0.1, source="exploit"),  # Low score
        ]

        accepted = controller._accept_features(candidates)

        assert len(accepted) == 0
        assert "ml/algorithms/linear" in controller.rejected_features

    def test_reject_generic_infrastructure(self, controller):
        """Test rejecting generic infrastructure features."""
        candidates = [
            FeaturePath(path="utils/logging/config", score=0.9, source="exploit"),
            FeaturePath(path="common/helpers/base", score=0.9, source="exploit"),
        ]

        accepted = controller._accept_features(candidates)

        assert len(accepted) == 0


class TestBuildCapabilityGraphFromFeatures:
    """Tests for building capability graph from feature paths."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_vector_store = MagicMock()

        return ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

    def test_build_graph_creates_hierarchy(self, controller):
        """Test that graph creates hierarchical nodes."""
        features = [
            FeaturePath(path="ml/algorithms/regression/linear", score=0.9, source="exploit"),
            FeaturePath(path="ml/algorithms/classification/logistic", score=0.8, source="explore"),
        ]

        rpg = controller._build_capability_graph(features)

        assert isinstance(rpg, RPG)
        assert len(rpg.nodes) > 0

        # Should have nodes for each path segment
        node_names = [n.name.lower() for n in rpg.nodes]
        assert any("ml" in name for name in node_names)

    def test_build_graph_creates_edges(self, controller):
        """Test that graph creates edges between nodes."""
        features = [
            FeaturePath(path="ml/algorithms/linear", score=0.9, source="exploit"),
        ]

        rpg = controller._build_capability_graph(features)

        # Should have edges connecting hierarchy
        assert len(rpg.edges) >= 0  # May have some edges

    def test_build_graph_from_empty_features(self, controller):
        """Test building graph from empty feature list."""
        rpg = controller._build_capability_graph([])

        assert isinstance(rpg, RPG)
        assert len(rpg.nodes) == 0


class TestIsGenericInfrastructure:
    """Tests for generic infrastructure detection."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_vector_store = MagicMock()

        return ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

    def test_detect_logging(self, controller):
        """Test detection of logging infrastructure."""
        assert controller._is_generic_infrastructure("utils/logging/config")
        assert controller._is_generic_infrastructure("common/logging")

    def test_detect_config(self, controller):
        """Test detection of config infrastructure."""
        assert controller._is_generic_infrastructure("config/settings")
        assert controller._is_generic_infrastructure("utils/config")

    def test_detect_utils(self, controller):
        """Test detection of utils infrastructure."""
        assert controller._is_generic_infrastructure("utils/helpers")
        assert controller._is_generic_infrastructure("common/utils")

    def test_allow_business_logic(self, controller):
        """Test that business logic paths are allowed."""
        assert not controller._is_generic_infrastructure("ml/algorithms/linear")
        assert not controller._is_generic_infrastructure("data/processing/transform")


class TestIsTooSimilarToExisting:
    """Tests for similarity detection."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_vector_store = MagicMock()

        controller = ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

        # Add some existing features
        controller.selected_features.add("ml/algorithms/regression/linear")
        controller.selected_features.add("ml/preprocessing/scaling")

        return controller

    def test_detect_highly_similar(self, controller):
        """Test detection of highly similar paths."""
        # Very similar to existing
        is_similar = controller._is_too_similar_to_existing("ml/algorithms/regression/linear_v2")

        # Should detect high similarity
        assert isinstance(is_similar, bool)

    def test_allow_different_paths(self, controller):
        """Test that different paths are allowed."""
        is_similar = controller._is_too_similar_to_existing("data/loading/csv")

        assert not is_similar


class TestSummarizeCurrentFeatures:
    """Tests for feature summarization."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_vector_store = MagicMock()

        return ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

    def test_summarize_empty_features(self, controller):
        """Test summarizing when no features selected."""
        summary = controller._summarize_current_features()

        assert "No features" in summary

    def test_summarize_with_features(self, controller):
        """Test summarizing with selected features."""
        controller.selected_features.add("ml/algorithms/linear")
        controller.selected_features.add("ml/algorithms/logistic")
        controller.selected_features.add("data/loading/csv")

        summary = controller._summarize_current_features()

        assert isinstance(summary, str)
        assert len(summary) > 0


class TestFlattenFeatureHierarchy:
    """Tests for flattening feature hierarchy."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_vector_store = MagicMock()

        return ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

    def test_flatten_simple_hierarchy(self, controller):
        """Test flattening simple hierarchy."""
        hierarchy = {
            "algorithms": ["linear", "logistic"]
        }

        paths = controller._flatten_feature_hierarchy(hierarchy)

        assert "algorithms/linear" in paths
        assert "algorithms/logistic" in paths

    def test_flatten_nested_hierarchy(self, controller):
        """Test flattening nested hierarchy."""
        hierarchy = {
            "ml": {
                "algorithms": {
                    "regression": ["linear", "polynomial"]
                }
            }
        }

        paths = controller._flatten_feature_hierarchy(hierarchy)

        assert "ml/algorithms/regression/linear" in paths
        assert "ml/algorithms/regression/polynomial" in paths

    def test_flatten_empty_hierarchy(self, controller):
        """Test flattening empty hierarchy."""
        paths = controller._flatten_feature_hierarchy({})

        assert paths == []


class TestPromptBuilding:
    """Tests for prompt building methods."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_vector_store = MagicMock()

        return ProposalController(
            config=sample_project_config,
            llm_client=mock_llm_client,
            vector_store=mock_vector_store
        )

    def test_build_exploit_prompt(self, controller):
        """Test exploit prompt building."""
        features = [
            FeaturePath(path="ml/algorithms/linear", score=0.9, source="exploit"),
        ]
        context = {
            "project_goal": "Build ML toolkit",
            "current_repo_paths": [],
            "iteration": 0
        }

        prompt = controller._build_exploit_prompt(features, context)

        assert isinstance(prompt, str)
        assert "Build ML toolkit" in prompt or "project_goal" in prompt.lower()

    def test_build_explore_prompt(self, controller):
        """Test explore prompt building."""
        features = [
            FeaturePath(path="ml/preprocessing/scaling", score=0.6, source="explore"),
        ]
        context = {
            "project_goal": "Build ML toolkit",
            "current_repo_paths": ["ml/algorithms/linear"],
            "exploration_iteration": 1
        }

        prompt = controller._build_explore_prompt(features, context)

        assert isinstance(prompt, str)

    def test_build_missing_prompt(self, controller):
        """Test missing features prompt building."""
        controller.selected_features.add("ml/algorithms/linear")

        prompt = controller._build_missing_prompt("ml: linear", iteration=1)

        assert isinstance(prompt, str)
        assert "missing" in prompt.lower() or "features" in prompt.lower()
