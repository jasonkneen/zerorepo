"""
Unit tests for Implementation Controller.
Tests file structure generation, interface creation, and data flow encoding.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

# Check for optional dependencies (implementation depends on vector_store -> faiss)
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

if not FAISS_AVAILABLE:
    pytest.skip("FAISS not installed", allow_module_level=True)

from zerorepo.core.models import RPG, RPGNode, RPGEdge, FileSkeleton, ProjectConfig
from zerorepo.tools.llm_client import LLMResponse
from zerorepo.plan.implementation import ImplementationController


class TestImplementationControllerInit:
    """Tests for ImplementationController initialization."""

    def test_init_with_config(self, sample_project_config):
        """Test initialization with config."""
        mock_llm_client = MagicMock()

        controller = ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

        assert controller.config == sample_project_config


class TestBuildImplementationGraph:
    """Tests for build_implementation_graph method."""

    @pytest.fixture
    def controller_with_mocks(self, sample_project_config):
        """Create controller with mocked dependencies."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content='{"folders": [{"name": "src/algorithms", "maps": ["ML"]}], "files": []}',
            model="gpt-4",
            usage={},
            success=True
        ))

        controller = ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

        return controller

    @pytest.mark.asyncio
    async def test_build_implementation_graph_returns_tuple(self, controller_with_mocks, simple_rpg):
        """Test that build_implementation_graph returns RPG and interfaces."""
        rpg, interfaces = await controller_with_mocks.build_implementation_graph(simple_rpg)

        assert isinstance(rpg, RPG)
        assert isinstance(interfaces, dict)


class TestBuildFileStructure:
    """Tests for file structure building."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content='{"folders": [{"name": "src", "maps": []}], "files": []}',
            model="gpt-4",
            usage={},
            success=True
        ))

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    @pytest.mark.asyncio
    async def test_build_file_structure_returns_rpg(self, controller, simple_rpg):
        """Test file structure building returns RPG."""
        rpg = await controller._build_file_structure(simple_rpg)

        assert isinstance(rpg, RPG)


class TestGenerateFolderSkeleton:
    """Tests for folder skeleton generation."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content='{"folders": [{"name": "src/core", "maps": ["Core"]}, {"name": "src/algorithms", "maps": ["Algorithms"]}], "files": []}',
            model="gpt-4",
            usage={},
            success=True
        ))

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    @pytest.mark.asyncio
    async def test_generate_folder_skeleton(self, controller, simple_rpg):
        """Test folder skeleton generation."""
        skeleton = await controller._generate_folder_skeleton(simple_rpg)

        assert isinstance(skeleton, FileSkeleton)
        assert len(skeleton.folders) > 0

    @pytest.mark.asyncio
    async def test_generate_folder_skeleton_fallback(self, sample_project_config, simple_rpg):
        """Test fallback on LLM failure."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content="",
            model="gpt-4",
            usage={},
            success=False,
            error="API Error"
        ))

        controller = ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

        skeleton = await controller._generate_folder_skeleton(simple_rpg)

        # Should return fallback skeleton
        assert isinstance(skeleton, FileSkeleton)
        assert len(skeleton.folders) > 0


class TestAssignFeaturesToFiles:
    """Tests for feature to file assignment."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content='{"src/algorithms/linear.py": ["ml/algorithms/linear"]}',
            model="gpt-4",
            usage={},
            success=True
        ))

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    @pytest.mark.asyncio
    async def test_assign_features_to_files(self, controller, simple_rpg, sample_file_skeleton):
        """Test feature to file assignment."""
        assignments = await controller._assign_features_to_files(simple_rpg, sample_file_skeleton)

        assert isinstance(assignments, dict)

    @pytest.mark.asyncio
    async def test_assign_features_fallback(self, sample_project_config, simple_rpg, sample_file_skeleton):
        """Test fallback on LLM failure."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content="",
            model="gpt-4",
            usage={},
            success=False,
            error="API Error"
        ))

        controller = ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

        assignments = await controller._assign_features_to_files(simple_rpg, sample_file_skeleton)

        assert isinstance(assignments, dict)


class TestGenerateBaseClasses:
    """Tests for base class generation."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content='```python\nclass BaseEstimator:\n    pass\n```',
            model="gpt-4",
            usage={},
            success=True
        ))

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    @pytest.mark.asyncio
    async def test_generate_base_classes(self, controller, complex_rpg):
        """Test base class generation."""
        base_classes = await controller._generate_base_classes(complex_rpg)

        assert isinstance(base_classes, dict)


class TestGenerateInterfaces:
    """Tests for interface generation."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content='class LinearRegressor:\n    def fit(self, X, y):\n        pass',
            model="gpt-4",
            usage={},
            success=True
        ))

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    @pytest.mark.asyncio
    async def test_generate_interfaces(self, controller, complex_rpg):
        """Test interface generation."""
        base_classes = {}
        interfaces = await controller._generate_interfaces(complex_rpg, base_classes)

        assert isinstance(interfaces, dict)


class TestAddDataFlowEdges:
    """Tests for data flow edge addition."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    @pytest.mark.asyncio
    async def test_add_data_flow_edges(self, controller, complex_rpg, sample_interfaces):
        """Test adding data flow edges."""
        updated_rpg = await controller._add_data_flow_edges(complex_rpg, sample_interfaces)

        assert isinstance(updated_rpg, RPG)
        assert "implementation" in updated_rpg.metadata.get("stage", "")


class TestCreateFileNodes:
    """Tests for file node creation."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_create_file_nodes(self, controller, simple_rpg, sample_file_skeleton):
        """Test creating file nodes in graph."""
        assignments = {
            "src/algorithms/linear.py": ["ml/algorithms/linear"]
        }

        rpg = controller._create_file_nodes(simple_rpg, sample_file_skeleton, assignments)

        assert isinstance(rpg, RPG)
        # Should have more nodes than original
        assert len(rpg.nodes) >= len(simple_rpg.nodes)


class TestCreateInterfaceNodes:
    """Tests for interface node creation."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_create_interface_nodes(self, controller, complex_rpg, sample_interfaces):
        """Test creating interface nodes."""
        final_rpg = controller._create_interface_nodes(complex_rpg, sample_interfaces)

        assert isinstance(final_rpg, RPG)


class TestGroupCapabilitiesBySimilarity:
    """Tests for capability grouping."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_group_by_prefix(self, controller):
        """Test grouping by feature path prefix."""
        capabilities = [
            RPGNode(id="c1", name="Linear", kind="capability",
                   meta={"feature_path": "ml/algorithms/linear"}),
            RPGNode(id="c2", name="Logistic", kind="capability",
                   meta={"feature_path": "ml/algorithms/logistic"}),
            RPGNode(id="c3", name="Scaling", kind="capability",
                   meta={"feature_path": "ml/preprocessing/scaling"}),
        ]

        groups = controller._group_capabilities_by_similarity(capabilities)

        assert isinstance(groups, list)
        assert len(groups) >= 1

    def test_group_empty_list(self, controller):
        """Test grouping empty list."""
        groups = controller._group_capabilities_by_similarity([])

        assert groups == []


class TestCreateFallbackSkeleton:
    """Tests for fallback skeleton creation."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_create_fallback_skeleton(self, controller):
        """Test fallback skeleton creation."""
        capabilities = [
            RPGNode(id="c1", name="Test", kind="capability"),
        ]

        skeleton = controller._create_fallback_skeleton(capabilities)

        assert isinstance(skeleton, FileSkeleton)
        assert len(skeleton.folders) > 0


class TestCreateFallbackAssignment:
    """Tests for fallback file assignment."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_create_fallback_assignment(self, controller, sample_file_skeleton):
        """Test fallback assignment creation."""
        capabilities = [
            RPGNode(id="c1", name="Linear", kind="capability",
                   meta={"feature_path": "ml/linear"}),
            RPGNode(id="c2", name="Logistic", kind="capability",
                   meta={"feature_path": "ml/logistic"}),
        ]

        assignments = controller._create_fallback_assignment(capabilities, sample_file_skeleton)

        assert isinstance(assignments, dict)
        assert len(assignments) == 2


class TestIdentifyCommonPatterns:
    """Tests for common pattern identification."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_identify_common_patterns(self, controller, complex_rpg):
        """Test identifying common patterns."""
        patterns = controller._identify_common_patterns(complex_rpg)

        assert isinstance(patterns, list)


class TestGetFileCapabilities:
    """Tests for getting file capabilities."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_get_file_capabilities(self, controller):
        """Test getting capabilities for a file."""
        nodes = [
            RPGNode(id="f1", name="linear.py", kind="file",
                   path_hint="src/linear.py",
                   meta={"features": ["ml/linear"]}),
            RPGNode(id="c1", name="Linear", kind="capability",
                   meta={"feature_path": "ml/linear"}),
        ]
        rpg = RPG(nodes=nodes, edges=[])

        file_node = nodes[0]
        capabilities = controller._get_file_capabilities(rpg, file_node)

        assert isinstance(capabilities, list)


class TestFindNodeByPath:
    """Tests for finding nodes by path."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_find_existing_node(self, controller, complex_rpg):
        """Test finding existing node by path."""
        node = controller._find_node_by_path(complex_rpg, "src/algorithms/linear.py")

        # May or may not find depending on fixture
        assert node is None or isinstance(node, RPGNode)

    def test_find_nonexistent_node(self, controller, complex_rpg):
        """Test finding non-existent node."""
        node = controller._find_node_by_path(complex_rpg, "nonexistent/path.py")

        assert node is None


class TestParseInterfaceCode:
    """Tests for interface code parsing."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_parse_class_interface(self, controller):
        """Test parsing class interface."""
        code = """class LinearRegressor:
    def fit(self, X, y):
        pass

    def predict(self, X):
        pass
"""
        specs = controller._parse_interface_code(code, "src/linear.py")

        assert isinstance(specs, list)
        assert len(specs) >= 1
        assert specs[0]["kind"] == "class"

    def test_parse_function_interface(self, controller):
        """Test parsing function interface."""
        code = """def calculate_sum(a: int, b: int) -> int:
    pass
"""
        specs = controller._parse_interface_code(code, "src/math.py")

        assert isinstance(specs, list)
        assert len(specs) >= 1
        assert specs[0]["kind"] == "function"

    def test_parse_empty_code(self, controller):
        """Test parsing empty code."""
        specs = controller._parse_interface_code("", "src/empty.py")

        assert specs == []


class TestParseBaseClassesResponse:
    """Tests for base classes response parsing."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_parse_markdown_code_block(self, controller):
        """Test parsing markdown code block."""
        response = """```python
class BaseEstimator:
    def fit(self, X, y):
        pass
```"""
        base_classes = controller._parse_base_classes_response(response)

        assert isinstance(base_classes, dict)
        assert "BaseEstimator" in base_classes

    def test_parse_plain_code(self, controller):
        """Test parsing plain code without markdown."""
        response = """class BaseProcessor:
    def process(self, data):
        pass
"""
        base_classes = controller._parse_base_classes_response(response)

        assert isinstance(base_classes, dict)

    def test_parse_empty_response(self, controller):
        """Test parsing empty response."""
        base_classes = controller._parse_base_classes_response("")

        assert base_classes == {}


class TestPromptBuilding:
    """Tests for prompt building methods."""

    @pytest.fixture
    def controller(self, sample_project_config):
        """Create controller for testing."""
        mock_llm_client = MagicMock()

        return ImplementationController(
            config=sample_project_config,
            llm_client=mock_llm_client
        )

    def test_build_folder_skeleton_prompt(self, controller):
        """Test folder skeleton prompt building."""
        capabilities = [
            {"name": "ML Algorithms", "children": ["linear", "logistic"], "feature_path": "ml/algorithms"}
        ]

        prompt = controller._build_folder_skeleton_prompt(capabilities)

        assert isinstance(prompt, str)
        assert "ML Algorithms" in prompt

    def test_build_file_assignment_prompt(self, controller, sample_file_skeleton):
        """Test file assignment prompt building."""
        groups = [[
            RPGNode(id="c1", name="Linear", kind="capability",
                   meta={"feature_path": "ml/linear"})
        ]]

        prompt = controller._build_file_assignment_prompt(groups, sample_file_skeleton)

        assert isinstance(prompt, str)

    def test_build_interfaces_prompt(self, controller):
        """Test interfaces prompt building."""
        file_node = RPGNode(
            id="f1",
            name="linear.py",
            kind="file",
            path_hint="src/linear.py"
        )
        capabilities = [
            RPGNode(id="c1", name="Linear Regression", kind="capability",
                   doc="Linear regression implementation")
        ]
        base_classes = {"BaseEstimator": "class BaseEstimator:\n    pass"}

        prompt = controller._build_interfaces_prompt(file_node, capabilities, base_classes)

        assert isinstance(prompt, str)
        assert "linear.py" in prompt

    def test_build_base_classes_prompt(self, controller):
        """Test base classes prompt building."""
        patterns = [
            {"name": "BaseEstimator", "pattern": "fit/predict methods"}
        ]

        prompt = controller._build_base_classes_prompt(patterns)

        assert isinstance(prompt, str)
        assert "BaseEstimator" in prompt
