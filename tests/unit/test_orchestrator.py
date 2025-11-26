"""
Unit tests for ZeroRepo Orchestrator.
Tests pipeline coordination and stage execution.
"""

import pytest
import os
from unittest.mock import MagicMock, AsyncMock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

# Check for optional dependencies (orchestrator depends on vector_store -> faiss)
try:
    import faiss
    import docker
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

if not DEPS_AVAILABLE:
    pytest.skip("faiss/docker not installed", allow_module_level=True)

from zerorepo.core.models import RPG, RPGNode, ProjectConfig, GenerationResult, FeaturePath
from zerorepo.tools.llm_client import LLMResponse


class TestZeroRepoOrchestratorInit:
    """Tests for ZeroRepoOrchestrator initialization."""

    @patch('zerorepo.orchestrator.LLMClient')
    @patch('zerorepo.orchestrator.VectorStore')
    @patch('zerorepo.orchestrator.DockerTestRunner')
    def test_init_with_api_key(self, mock_docker, mock_vector, mock_llm, sample_project_config):
        """Test initialization with API key."""
        from zerorepo.orchestrator import ZeroRepoOrchestrator

        orchestrator = ZeroRepoOrchestrator(
            config=sample_project_config,
            emergent_api_key="test-api-key"
        )

        assert orchestrator.config == sample_project_config
        mock_llm.assert_called_once()

    @patch('zerorepo.orchestrator.LLMClient')
    @patch('zerorepo.orchestrator.VectorStore')
    @patch('zerorepo.orchestrator.DockerTestRunner')
    def test_init_with_env_api_key(self, mock_docker, mock_vector, mock_llm, sample_project_config):
        """Test initialization with environment API key."""
        from zerorepo.orchestrator import ZeroRepoOrchestrator

        with patch.dict(os.environ, {"EMERGENT_LLM_KEY": "env-test-key"}):
            orchestrator = ZeroRepoOrchestrator(config=sample_project_config)

            assert orchestrator.config == sample_project_config

    def test_init_without_api_key_raises(self, sample_project_config):
        """Test that initialization without API key raises error."""
        from zerorepo.orchestrator import ZeroRepoOrchestrator

        with patch.dict(os.environ, {"EMERGENT_LLM_KEY": "", "OPENAI_API_KEY": ""}):
            with pytest.raises(ValueError):
                ZeroRepoOrchestrator(config=sample_project_config)


class TestRunFullPipeline:
    """Tests for full pipeline execution."""

    @pytest.fixture
    def mock_orchestrator(self, sample_project_config):
        """Create mock orchestrator."""
        with patch('zerorepo.orchestrator.LLMClient') as mock_llm, \
             patch('zerorepo.orchestrator.VectorStore') as mock_vector, \
             patch('zerorepo.orchestrator.DockerTestRunner') as mock_docker:

            # Setup vector store mock
            mock_vector_instance = MagicMock()
            mock_vector_instance.feature_paths = []
            mock_vector_instance.create_sample_ontology.return_value = {"ml": {"test": []}}
            mock_vector_instance.build_from_ontology = MagicMock()
            mock_vector.return_value = mock_vector_instance

            # Setup LLM mock
            mock_llm_instance = MagicMock()
            mock_llm_instance.generate = AsyncMock(return_value=LLMResponse(
                content='{"test": "data"}',
                model="gpt-4",
                usage={},
                success=True
            ))
            mock_llm_instance.generate_json = AsyncMock(return_value={
                "all_selected_feature_paths": []
            })
            mock_llm.return_value = mock_llm_instance

            from zerorepo.orchestrator import ZeroRepoOrchestrator
            orchestrator = ZeroRepoOrchestrator(
                config=sample_project_config,
                emergent_api_key="test-key"
            )

            return orchestrator

    @pytest.mark.asyncio
    async def test_run_full_pipeline_returns_result(self, mock_orchestrator, temp_output_dir):
        """Test full pipeline returns GenerationResult."""
        # Mock the internal methods
        mock_orchestrator.run_proposal_stage = AsyncMock(return_value=(
            RPG(nodes=[], edges=[]),
            []
        ))
        mock_orchestrator.run_implementation_and_codegen_stages = AsyncMock(
            return_value=GenerationResult(success=True)
        )

        result = await mock_orchestrator.run_full_pipeline(temp_output_dir)

        assert isinstance(result, GenerationResult)

    @pytest.mark.asyncio
    async def test_run_full_pipeline_handles_error(self, mock_orchestrator, temp_output_dir):
        """Test full pipeline handles errors gracefully."""
        mock_orchestrator.run_proposal_stage = AsyncMock(
            side_effect=Exception("Pipeline error")
        )

        result = await mock_orchestrator.run_full_pipeline(temp_output_dir)

        assert result.success is False
        assert len(result.errors) > 0


class TestRunProposalStage:
    """Tests for proposal stage execution."""

    @pytest.fixture
    def mock_orchestrator(self, sample_project_config):
        """Create mock orchestrator."""
        with patch('zerorepo.orchestrator.LLMClient') as mock_llm, \
             patch('zerorepo.orchestrator.VectorStore') as mock_vector, \
             patch('zerorepo.orchestrator.DockerTestRunner'):

            mock_vector_instance = MagicMock()
            mock_vector_instance.feature_paths = []
            mock_vector_instance.create_sample_ontology.return_value = {"ml": {"test": []}}
            mock_vector_instance.build_from_ontology = MagicMock()
            mock_vector.return_value = mock_vector_instance

            mock_llm_instance = MagicMock()
            mock_llm_instance.generate_json = AsyncMock(return_value={
                "all_selected_feature_paths": []
            })
            mock_llm.return_value = mock_llm_instance

            from zerorepo.orchestrator import ZeroRepoOrchestrator
            orchestrator = ZeroRepoOrchestrator(
                config=sample_project_config,
                emergent_api_key="test-key"
            )

            # Mock proposal controller
            orchestrator.proposal_controller.build_capability_graph = AsyncMock(
                return_value=(
                    RPG(nodes=[RPGNode(id="test", name="Test", kind="capability")], edges=[]),
                    [FeaturePath(path="test", score=0.9, source="exploit")]
                )
            )

            return orchestrator

    @pytest.mark.asyncio
    async def test_run_proposal_stage_initializes_vector_store(self, mock_orchestrator):
        """Test proposal stage initializes vector store if empty."""
        rpg, features = await mock_orchestrator.run_proposal_stage()

        assert isinstance(rpg, RPG)
        assert isinstance(features, list)

    @pytest.mark.asyncio
    async def test_run_proposal_stage_returns_graph(self, mock_orchestrator):
        """Test proposal stage returns capability graph."""
        rpg, features = await mock_orchestrator.run_proposal_stage()

        assert len(rpg.nodes) > 0


class TestRunImplementationAndCodegenStages:
    """Tests for implementation and codegen stages."""

    @pytest.fixture
    def mock_orchestrator(self, sample_project_config):
        """Create mock orchestrator."""
        with patch('zerorepo.orchestrator.LLMClient') as mock_llm, \
             patch('zerorepo.orchestrator.VectorStore') as mock_vector, \
             patch('zerorepo.orchestrator.DockerTestRunner') as mock_docker:

            mock_vector_instance = MagicMock()
            mock_vector.return_value = mock_vector_instance

            mock_llm_instance = MagicMock()
            mock_llm_instance.generate = AsyncMock(return_value=LLMResponse(
                content="test",
                model="gpt-4",
                usage={},
                success=True
            ))
            mock_llm.return_value = mock_llm_instance

            mock_docker_instance = MagicMock()
            mock_docker_instance.run_tests = AsyncMock(return_value={"success": True})
            mock_docker_instance.run_all_tests = AsyncMock(return_value={"success": True})
            mock_docker.return_value = mock_docker_instance

            from zerorepo.orchestrator import ZeroRepoOrchestrator
            orchestrator = ZeroRepoOrchestrator(
                config=sample_project_config,
                emergent_api_key="test-key"
            )

            # Mock controllers
            orchestrator.implementation_controller.build_implementation_graph = AsyncMock(
                return_value=(RPG(nodes=[], edges=[]), {})
            )
            orchestrator.code_generator.generate_repository = AsyncMock(
                return_value=GenerationResult(success=True)
            )

            return orchestrator

    @pytest.mark.asyncio
    async def test_run_implementation_and_codegen(self, mock_orchestrator, simple_rpg, temp_output_dir):
        """Test implementation and codegen stages."""
        result = await mock_orchestrator.run_implementation_and_codegen_stages(
            simple_rpg,
            temp_output_dir
        )

        assert isinstance(result, GenerationResult)


class TestValidatePipelinePrerequisites:
    """Tests for prerequisite validation."""

    @pytest.fixture
    def mock_orchestrator(self, sample_project_config):
        """Create mock orchestrator."""
        with patch('zerorepo.orchestrator.LLMClient') as mock_llm, \
             patch('zerorepo.orchestrator.VectorStore') as mock_vector, \
             patch('zerorepo.orchestrator.DockerTestRunner'):

            mock_vector_instance = MagicMock()
            mock_vector_instance.feature_paths = []
            mock_vector_instance.create_sample_ontology.return_value = {"ml": {}}
            mock_vector_instance.build_from_ontology = MagicMock()
            mock_vector_instance.get_stats.return_value = {"total_features": 10}
            mock_vector.return_value = mock_vector_instance

            mock_llm_instance = MagicMock()
            mock_llm_instance.generate = AsyncMock(return_value=LLMResponse(
                content="test",
                model="gpt-4",
                usage={},
                success=True
            ))
            mock_llm.return_value = mock_llm_instance

            from zerorepo.orchestrator import ZeroRepoOrchestrator
            orchestrator = ZeroRepoOrchestrator(
                config=sample_project_config,
                emergent_api_key="test-key"
            )

            return orchestrator

    @pytest.mark.asyncio
    async def test_validate_prerequisites_all_pass(self, mock_orchestrator):
        """Test validation when all prerequisites pass."""
        is_valid = await mock_orchestrator.validate_pipeline_prerequisites()

        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_prerequisites_llm_fails(self, sample_project_config):
        """Test validation when LLM check fails."""
        with patch('zerorepo.orchestrator.LLMClient') as mock_llm, \
             patch('zerorepo.orchestrator.VectorStore') as mock_vector, \
             patch('zerorepo.orchestrator.DockerTestRunner'):

            mock_vector_instance = MagicMock()
            mock_vector_instance.feature_paths = [1]  # Non-empty
            mock_vector_instance.get_stats.return_value = {"total_features": 1}
            mock_vector.return_value = mock_vector_instance

            mock_llm_instance = MagicMock()
            mock_llm_instance.generate = AsyncMock(
                side_effect=Exception("LLM Error")
            )
            mock_llm.return_value = mock_llm_instance

            from zerorepo.orchestrator import ZeroRepoOrchestrator
            orchestrator = ZeroRepoOrchestrator(
                config=sample_project_config,
                emergent_api_key="test-key"
            )

            is_valid = await orchestrator.validate_pipeline_prerequisites()

            assert is_valid is False


class TestGetPipelineStatus:
    """Tests for pipeline status retrieval."""

    @pytest.fixture
    def mock_orchestrator(self, sample_project_config):
        """Create mock orchestrator."""
        with patch('zerorepo.orchestrator.LLMClient'), \
             patch('zerorepo.orchestrator.VectorStore') as mock_vector, \
             patch('zerorepo.orchestrator.DockerTestRunner'):

            mock_vector_instance = MagicMock()
            mock_vector_instance.get_stats.return_value = {
                "total_features": 100,
                "index_size": 100
            }
            mock_vector.return_value = mock_vector_instance

            from zerorepo.orchestrator import ZeroRepoOrchestrator
            orchestrator = ZeroRepoOrchestrator(
                config=sample_project_config,
                emergent_api_key="test-key"
            )

            return orchestrator

    def test_get_pipeline_status(self, mock_orchestrator):
        """Test pipeline status retrieval."""
        status = mock_orchestrator.get_pipeline_status()

        assert "config" in status
        assert "vector_store" in status
        assert "components" in status
        assert status["config"]["project_goal"] == mock_orchestrator.config.project_goal


class TestCleanup:
    """Tests for cleanup functionality."""

    @pytest.fixture
    def mock_orchestrator(self, sample_project_config):
        """Create mock orchestrator."""
        with patch('zerorepo.orchestrator.LLMClient'), \
             patch('zerorepo.orchestrator.VectorStore'), \
             patch('zerorepo.orchestrator.DockerTestRunner') as mock_docker:

            mock_docker_instance = MagicMock()
            mock_docker_instance.cleanup = MagicMock()
            mock_docker.return_value = mock_docker_instance

            from zerorepo.orchestrator import ZeroRepoOrchestrator
            orchestrator = ZeroRepoOrchestrator(
                config=sample_project_config,
                emergent_api_key="test-key"
            )

            return orchestrator

    @pytest.mark.asyncio
    async def test_cleanup_calls_docker_cleanup(self, mock_orchestrator):
        """Test cleanup calls Docker runner cleanup."""
        await mock_orchestrator.cleanup()

        mock_orchestrator.docker_runner.cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_handles_errors(self, mock_orchestrator):
        """Test cleanup handles errors gracefully."""
        mock_orchestrator.docker_runner.cleanup.side_effect = Exception("Cleanup error")

        # Should not raise
        await mock_orchestrator.cleanup()


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    @patch('zerorepo.orchestrator.ZeroRepoOrchestrator')
    async def test_generate_repository_function(self, mock_orchestrator_class, temp_output_dir):
        """Test generate_repository convenience function."""
        mock_instance = MagicMock()
        mock_instance.validate_pipeline_prerequisites = AsyncMock(return_value=True)
        mock_instance.run_full_pipeline = AsyncMock(
            return_value=GenerationResult(success=True)
        )
        mock_instance.cleanup = AsyncMock()
        mock_orchestrator_class.return_value = mock_instance

        from zerorepo.orchestrator import generate_repository

        result = await generate_repository(
            project_goal="Test project",
            output_dir=temp_output_dir,
            domain="ml",
            emergent_api_key="test-key"
        )

        assert isinstance(result, GenerationResult)

    @pytest.mark.asyncio
    @patch('zerorepo.orchestrator.ZeroRepoOrchestrator')
    async def test_generate_repository_prerequisite_fail(self, mock_orchestrator_class, temp_output_dir):
        """Test generate_repository when prerequisites fail."""
        mock_instance = MagicMock()
        mock_instance.validate_pipeline_prerequisites = AsyncMock(return_value=False)
        mock_instance.cleanup = AsyncMock()
        mock_orchestrator_class.return_value = mock_instance

        from zerorepo.orchestrator import generate_repository

        result = await generate_repository(
            project_goal="Test project",
            output_dir=temp_output_dir,
            emergent_api_key="test-key"
        )

        assert result.success is False

    @pytest.mark.asyncio
    @patch('zerorepo.orchestrator.ZeroRepoOrchestrator')
    async def test_plan_repository_function(self, mock_orchestrator_class):
        """Test plan_repository convenience function."""
        mock_instance = MagicMock()
        mock_instance.run_proposal_stage = AsyncMock(return_value=(
            RPG(nodes=[RPGNode(id="test", name="Test", kind="capability")], edges=[]),
            [FeaturePath(path="test", score=0.9, source="exploit")]
        ))
        mock_instance.cleanup = AsyncMock()
        mock_orchestrator_class.return_value = mock_instance

        from zerorepo.orchestrator import plan_repository

        rpg, features = await plan_repository(
            project_goal="Test project",
            domain="ml",
            emergent_api_key="test-key"
        )

        assert isinstance(rpg, RPG)
        assert isinstance(features, list)
