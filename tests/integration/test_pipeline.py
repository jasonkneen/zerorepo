"""
Integration tests for ZeroRepo pipeline.
Tests end-to-end workflow and component integration.
"""

import pytest
import os
import tempfile
from unittest.mock import MagicMock, AsyncMock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

# Check for optional dependencies
try:
    import faiss
    import docker
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

if not DEPS_AVAILABLE:
    pytest.skip("faiss/docker not installed", allow_module_level=True)

from zerorepo.core.models import RPG, RPGNode, RPGEdge, FeaturePath, ProjectConfig, GenerationResult
from zerorepo.tools.llm_client import LLMResponse


@pytest.mark.integration
class TestProposalToImplementationIntegration:
    """Tests for proposal to implementation stage integration."""

    @pytest.fixture
    def project_config(self):
        """Create project configuration."""
        return ProjectConfig(
            project_goal="Build a simple calculator",
            domain="general",
            max_iterations=2,
            llm_model="gpt-4o-mini"
        )

    @pytest.mark.asyncio
    async def test_proposal_output_compatible_with_implementation(self, project_config):
        """Test proposal output is compatible with implementation input."""
        with patch('zerorepo.tools.llm_client.AsyncOpenAI'), \
             patch('zerorepo.tools.vector_store.SentenceTransformer'), \
             patch('zerorepo.tools.vector_store.faiss'):

            from zerorepo.plan.proposal import ProposalController
            from zerorepo.plan.implementation import ImplementationController

            # Create mock LLM client
            mock_llm = MagicMock()
            mock_llm.generate_json = AsyncMock(return_value={
                "all_selected_feature_paths": ["math/operations/add"]
            })
            mock_llm.generate = AsyncMock(return_value=LLMResponse(
                content='{"folders": [{"name": "src", "maps": []}], "files": []}',
                model="gpt-4",
                usage={},
                success=True
            ))

            # Create mock vector store
            mock_vector_store = MagicMock()
            mock_vector_store.search_features = AsyncMock(return_value=[
                FeaturePath(path="math/operations", score=0.9, source="exploit")
            ])
            mock_vector_store.sample_diverse_features = AsyncMock(return_value=[])

            # Create proposal controller
            proposal_controller = ProposalController(
                config=project_config,
                llm_client=mock_llm,
                vector_store=mock_vector_store
            )

            # Build capability graph
            capability_graph, features = await proposal_controller.build_capability_graph()

            # Verify output
            assert isinstance(capability_graph, RPG)

            # Create implementation controller
            impl_controller = ImplementationController(
                config=project_config,
                llm_client=mock_llm
            )

            # Should accept capability graph as input
            impl_graph, interfaces = await impl_controller.build_implementation_graph(capability_graph)

            assert isinstance(impl_graph, RPG)
            assert isinstance(interfaces, dict)


@pytest.mark.integration
class TestImplementationToCodegenIntegration:
    """Tests for implementation to codegen stage integration."""

    @pytest.fixture
    def project_config(self):
        """Create project configuration."""
        return ProjectConfig(
            project_goal="Build test project",
            domain="general",
            max_retries=1
        )

    @pytest.mark.asyncio
    async def test_implementation_output_compatible_with_codegen(self, project_config):
        """Test implementation output is compatible with codegen input."""
        # Create a simple implementation graph
        impl_graph = RPG(
            nodes=[
                RPGNode(id="folder-1", name="src", kind="folder", path_hint="src/"),
                RPGNode(id="file-1", name="main.py", kind="file", path_hint="src/main.py"),
                RPGNode(id="func-1", name="main", kind="function",
                       path_hint="src/main.py",
                       signature="def main():",
                       doc="Main function"),
            ],
            edges=[
                RPGEdge(from_node="folder-1", to_node="file-1", type="order"),
                RPGEdge(from_node="file-1", to_node="func-1", type="depends_on"),
            ]
        )

        interfaces = {
            "src/main.py": "def main():\n    pass"
        }

        # Create mock dependencies
        mock_llm = MagicMock()
        mock_llm.generate = AsyncMock(return_value=LLMResponse(
            content='```python\ndef main():\n    print("Hello")\n```',
            model="gpt-4",
            usage={},
            success=True
        ))

        mock_docker = MagicMock()
        mock_docker.run_tests = AsyncMock(return_value={"success": True, "exit_code": 0})
        mock_docker.run_all_tests = AsyncMock(return_value={
            "success": True,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        })

        from zerorepo.codegen.generator import CodeGenerator

        code_generator = CodeGenerator(
            config=project_config,
            llm_client=mock_llm,
            docker_runner=mock_docker
        )

        with tempfile.TemporaryDirectory() as output_dir:
            result = await code_generator.generate_repository(
                impl_graph,
                interfaces,
                output_dir
            )

            assert isinstance(result, GenerationResult)


@pytest.mark.integration
class TestGraphOpsWithRealRPG:
    """Tests for graph operations with realistic RPG data."""

    def test_topological_sort_on_realistic_graph(self):
        """Test topological sort on realistic graph."""
        from zerorepo.rpg.graph_ops import RPGGraphOps

        # Create realistic RPG structure
        nodes = [
            RPGNode(id="base", name="BaseClass", kind="class",
                   path_hint="src/base.py",
                   signature="class BaseClass:",
                   doc="Base class"),
            RPGNode(id="derived1", name="DerivedClass1", kind="class",
                   path_hint="src/derived1.py",
                   signature="class DerivedClass1(BaseClass):",
                   doc="First derived class"),
            RPGNode(id="derived2", name="DerivedClass2", kind="class",
                   path_hint="src/derived2.py",
                   signature="class DerivedClass2(BaseClass):",
                   doc="Second derived class"),
            RPGNode(id="consumer", name="Consumer", kind="class",
                   path_hint="src/consumer.py",
                   signature="class Consumer:",
                   doc="Consumes derived classes"),
        ]

        edges = [
            RPGEdge(from_node="base", to_node="derived1", type="data_flow"),
            RPGEdge(from_node="base", to_node="derived2", type="data_flow"),
            RPGEdge(from_node="derived1", to_node="consumer", type="data_flow"),
            RPGEdge(from_node="derived2", to_node="consumer", type="data_flow"),
        ]

        rpg = RPG(nodes=nodes, edges=edges)
        ops = RPGGraphOps(rpg)

        order = ops.topological_sort()

        # Base should come before derived classes
        if "base" in order and "derived1" in order:
            assert order.index("base") < order.index("derived1")
        if "base" in order and "derived2" in order:
            assert order.index("base") < order.index("derived2")

    def test_validate_dag_on_complex_graph(self):
        """Test DAG validation on complex graph."""
        from zerorepo.rpg.graph_ops import RPGGraphOps

        # Create complex but valid DAG
        nodes = []
        edges = []

        # Create 10 nodes with various relationships
        for i in range(10):
            nodes.append(RPGNode(
                id=f"node-{i}",
                name=f"Node{i}",
                kind="function" if i > 5 else "capability",
                path_hint=f"src/module{i}.py" if i > 5 else None
            ))

        # Create edges ensuring no cycles
        for i in range(9):
            edges.append(RPGEdge(
                from_node=f"node-{i}",
                to_node=f"node-{i+1}",
                type="data_flow"
            ))

        rpg = RPG(nodes=nodes, edges=edges)
        ops = RPGGraphOps(rpg)

        is_valid, errors = ops.validate_dag()

        assert is_valid is True


@pytest.mark.integration
class TestVectorStoreWithOntology:
    """Tests for vector store with ontology data."""

    def test_ontology_loading_and_search(self):
        """Test loading ontology and searching."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            # Setup mocks
            mock_encoder = MagicMock()
            mock_encoder.encode.return_value = \
                __import__('numpy').random.rand(100, 384).astype(__import__('numpy').float32)
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 0
            mock_faiss.IndexFlatIP.return_value = mock_index
            mock_faiss.normalize_L2 = MagicMock()

            from zerorepo.tools.vector_store import VectorStore

            store = VectorStore()

            # Create and load ontology
            ontology = store.create_sample_ontology()
            store.build_from_ontology(ontology)

            # Should have features
            assert len(store.feature_paths) > 0

            # Test stats
            stats = store.get_stats()
            assert stats["total_features"] > 0


@pytest.mark.integration
class TestFullPipelineWithMocks:
    """Tests for full pipeline with mocked external dependencies."""

    @pytest.fixture
    def mock_dependencies(self):
        """Setup mock dependencies."""
        with patch('zerorepo.orchestrator.LLMClient') as mock_llm_class, \
             patch('zerorepo.orchestrator.VectorStore') as mock_vector_class, \
             patch('zerorepo.orchestrator.DockerTestRunner') as mock_docker_class:

            # LLM mock
            mock_llm = MagicMock()
            mock_llm.generate = AsyncMock(return_value=LLMResponse(
                content='{"test": "data"}',
                model="gpt-4",
                usage={},
                success=True
            ))
            mock_llm.generate_json = AsyncMock(return_value={
                "all_selected_feature_paths": ["test/feature"]
            })
            mock_llm_class.return_value = mock_llm

            # Vector store mock
            mock_vector = MagicMock()
            mock_vector.feature_paths = []
            mock_vector.create_sample_ontology.return_value = {"test": {}}
            mock_vector.build_from_ontology = MagicMock()
            mock_vector.search_features = AsyncMock(return_value=[])
            mock_vector.sample_diverse_features = AsyncMock(return_value=[])
            mock_vector.get_stats.return_value = {"total_features": 10}
            mock_vector_class.return_value = mock_vector

            # Docker mock
            mock_docker = MagicMock()
            mock_docker.run_tests = AsyncMock(return_value={"success": True})
            mock_docker.run_all_tests = AsyncMock(return_value={
                "success": True,
                "total_tests": 1,
                "passed_tests": 1,
                "failed_tests": 0
            })
            mock_docker.cleanup = MagicMock()
            mock_docker_class.return_value = mock_docker

            yield {
                "llm": mock_llm,
                "vector": mock_vector,
                "docker": mock_docker
            }

    @pytest.mark.asyncio
    async def test_full_pipeline_flow(self, mock_dependencies):
        """Test full pipeline from start to finish."""
        from zerorepo.orchestrator import ZeroRepoOrchestrator

        config = ProjectConfig(
            project_goal="Test project",
            domain="general",
            max_iterations=1
        )

        orchestrator = ZeroRepoOrchestrator(
            config=config,
            emergent_api_key="test-key"
        )

        with tempfile.TemporaryDirectory() as output_dir:
            # Run proposal stage
            rpg, features = await orchestrator.run_proposal_stage()

            assert isinstance(rpg, RPG)
            assert isinstance(features, list)

            # Cleanup
            await orchestrator.cleanup()


@pytest.mark.integration
class TestErrorRecovery:
    """Tests for error recovery in pipeline."""

    @pytest.mark.asyncio
    async def test_pipeline_handles_llm_errors(self):
        """Test pipeline handles LLM errors gracefully."""
        with patch('zerorepo.orchestrator.LLMClient') as mock_llm_class, \
             patch('zerorepo.orchestrator.VectorStore') as mock_vector_class, \
             patch('zerorepo.orchestrator.DockerTestRunner'):

            # LLM that fails
            mock_llm = MagicMock()
            mock_llm.generate = AsyncMock(side_effect=Exception("LLM Error"))
            mock_llm.generate_json = AsyncMock(side_effect=Exception("LLM Error"))
            mock_llm_class.return_value = mock_llm

            # Vector store
            mock_vector = MagicMock()
            mock_vector.feature_paths = []
            mock_vector.create_sample_ontology.return_value = {}
            mock_vector.build_from_ontology = MagicMock()
            mock_vector.search_features = AsyncMock(return_value=[])
            mock_vector.sample_diverse_features = AsyncMock(return_value=[])
            mock_vector_class.return_value = mock_vector

            from zerorepo.orchestrator import ZeroRepoOrchestrator

            config = ProjectConfig(
                project_goal="Test",
                max_iterations=1
            )

            orchestrator = ZeroRepoOrchestrator(
                config=config,
                emergent_api_key="test-key"
            )

            # Should not crash, but may return empty results
            rpg, features = await orchestrator.run_proposal_stage()

            assert isinstance(rpg, RPG)

            await orchestrator.cleanup()


@pytest.mark.integration
class TestConfigurationVariations:
    """Tests for different configuration variations."""

    @pytest.mark.asyncio
    async def test_ml_domain_configuration(self):
        """Test ML domain configuration."""
        config = ProjectConfig(
            project_goal="Build ML toolkit",
            domain="ml",
            llm_model="gpt-4o-mini",
            max_iterations=1
        )

        assert config.domain == "ml"

    @pytest.mark.asyncio
    async def test_web_domain_configuration(self):
        """Test web domain configuration."""
        config = ProjectConfig(
            project_goal="Build web API",
            domain="web",
            max_iterations=1
        )

        assert config.domain == "web"

    @pytest.mark.asyncio
    async def test_custom_model_configuration(self):
        """Test custom model configuration."""
        config = ProjectConfig(
            project_goal="Test",
            llm_model="claude-3-sonnet",
            temperature=0.5
        )

        assert config.llm_model == "claude-3-sonnet"
        assert config.temperature == 0.5
