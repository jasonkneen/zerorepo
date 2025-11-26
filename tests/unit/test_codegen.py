"""
Unit tests for Code Generator.
Tests TDD cycle, code extraction, and generation workflow.
"""

import pytest
import os
import tempfile
from unittest.mock import MagicMock, AsyncMock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

# Check for optional dependencies (codegen depends on docker_runtime -> docker)
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

if not DOCKER_AVAILABLE:
    pytest.skip("docker not installed", allow_module_level=True)

from zerorepo.core.models import RPG, RPGNode, RPGEdge, ProjectConfig, GenerationResult
from zerorepo.tools.llm_client import LLMResponse
from zerorepo.codegen.generator import CodeGenerator


class TestCodeGeneratorInit:
    """Tests for CodeGenerator initialization."""

    def test_init_with_dependencies(self, sample_project_config, mock_llm_client, mock_docker_runner):
        """Test initialization with dependencies."""
        generator = CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

        assert generator.config == sample_project_config
        assert generator.generated_files == set()
        assert generator.failed_files == set()


class TestExtractCodeBlock:
    """Tests for code block extraction."""

    @pytest.fixture
    def generator(self, sample_project_config, mock_llm_client, mock_docker_runner):
        """Create generator for testing."""
        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    def test_extract_python_code_block(self, generator):
        """Test extracting Python code block."""
        content = '''Here's the code:
```python
def hello():
    print("Hello, World!")
```
That's the implementation.'''

        result = generator._extract_code_block(content)

        assert "def hello" in result
        assert "```" not in result

    def test_extract_generic_code_block(self, generator):
        """Test extracting generic code block."""
        content = '''Here's the code:
```
def hello():
    return 42
```'''

        result = generator._extract_code_block(content)

        assert "def hello" in result

    def test_extract_from_raw_code(self, generator):
        """Test extracting when content is raw code."""
        content = '''def hello():
    print("Hello, World!")'''

        result = generator._extract_code_block(content)

        assert "def hello" in result

    def test_extract_empty_content(self, generator):
        """Test extracting from empty content."""
        result = generator._extract_code_block("")

        assert result == ""

    def test_extract_no_code_block(self, generator):
        """Test extracting when no code block found."""
        content = "Here is the implementation of the function."

        result = generator._extract_code_block(content)

        # Should return empty since it looks like explanation text
        assert result == ""


class TestGenerateRepository:
    """Tests for repository generation."""

    @pytest.fixture
    def generator_with_mocks(self, sample_project_config):
        """Create generator with mocked dependencies."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content='```python\ndef test_func():\n    pass\n```',
            model="gpt-4",
            usage={},
            success=True
        ))

        mock_docker_runner = MagicMock()
        mock_docker_runner.run_tests = AsyncMock(return_value={
            "success": True,
            "output": "1 passed",
            "exit_code": 0
        })
        mock_docker_runner.run_all_tests = AsyncMock(return_value={
            "success": True,
            "total_tests": 1,
            "passed_tests": 1,
            "failed_tests": 0
        })

        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    @pytest.mark.asyncio
    async def test_generate_repository_returns_result(self, generator_with_mocks, complex_rpg, sample_interfaces, temp_output_dir):
        """Test repository generation returns GenerationResult."""
        result = await generator_with_mocks.generate_repository(
            complex_rpg,
            sample_interfaces,
            temp_output_dir
        )

        assert isinstance(result, GenerationResult)

    @pytest.mark.asyncio
    async def test_generate_creates_directory_structure(self, generator_with_mocks, complex_rpg, sample_interfaces, temp_output_dir):
        """Test that generation creates directory structure."""
        await generator_with_mocks.generate_repository(
            complex_rpg,
            sample_interfaces,
            temp_output_dir
        )

        # Tests directory should be created
        assert os.path.exists(os.path.join(temp_output_dir, "tests"))


class TestGenerateNodeCode:
    """Tests for individual node code generation."""

    @pytest.fixture
    def generator(self, sample_project_config, mock_llm_client, mock_docker_runner):
        """Create generator for testing."""
        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    @pytest.mark.asyncio
    async def test_generate_node_code_success(self, sample_project_config, temp_output_dir):
        """Test successful node code generation."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content='```python\ndef test_func():\n    assert True\n```',
            model="gpt-4",
            usage={},
            success=True
        ))

        mock_docker_runner = MagicMock()
        mock_docker_runner.run_tests = AsyncMock(return_value={
            "success": True,
            "output": "1 passed",
            "exit_code": 0
        })

        generator = CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

        node = RPGNode(
            id="func-1",
            name="test_function",
            kind="function",
            path_hint="src/test.py",
            signature="def test_function():",
            doc="A test function"
        )
        rpg = RPG(nodes=[node], edges=[])
        interfaces = {"src/test.py": "def test_function(): pass"}

        from zerorepo.rpg.graph_ops import RPGGraphOps
        graph_ops = RPGGraphOps(rpg)

        success = await generator._generate_node_code(
            node, rpg, interfaces, temp_output_dir, graph_ops
        )

        assert success is True


class TestGenerateUnitTest:
    """Tests for unit test generation."""

    @pytest.fixture
    def generator(self, sample_project_config):
        """Create generator for testing."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content='```python\nimport pytest\n\ndef test_linear():\n    assert True\n```',
            model="gpt-4",
            usage={},
            success=True
        ))

        mock_docker_runner = MagicMock()

        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    @pytest.mark.asyncio
    async def test_generate_unit_test_returns_code(self, generator):
        """Test unit test generation returns code."""
        node = RPGNode(
            id="func-1",
            name="calculate_sum",
            kind="function",
            path_hint="src/math.py",
            signature="def calculate_sum(a: int, b: int) -> int:",
            doc="Calculates sum of two integers"
        )
        interfaces = {"src/math.py": "def calculate_sum(a: int, b: int) -> int: pass"}

        test_code = await generator._generate_unit_test(node, interfaces)

        assert isinstance(test_code, str)
        assert len(test_code) > 0

    @pytest.mark.asyncio
    async def test_generate_unit_test_handles_failure(self, sample_project_config):
        """Test unit test generation handles LLM failure."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content="",
            model="gpt-4",
            usage={},
            success=False,
            error="API Error"
        ))

        mock_docker_runner = MagicMock()

        generator = CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

        node = RPGNode(
            id="func-1",
            name="test_func",
            kind="function",
            path_hint="src/test.py",
            signature="def test_func():",
            doc="Test"
        )

        test_code = await generator._generate_unit_test(node, {})

        assert test_code == ""


class TestGenerateImplementation:
    """Tests for implementation generation."""

    @pytest.fixture
    def generator(self, sample_project_config):
        """Create generator for testing."""
        mock_llm_client = MagicMock()
        mock_llm_client.generate = AsyncMock(return_value=LLMResponse(
            content='```python\ndef calculate_sum(a: int, b: int) -> int:\n    return a + b\n```',
            model="gpt-4",
            usage={},
            success=True
        ))

        mock_docker_runner = MagicMock()

        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    @pytest.mark.asyncio
    async def test_generate_implementation_returns_code(self, generator):
        """Test implementation generation returns code."""
        node = RPGNode(
            id="func-1",
            name="calculate_sum",
            kind="function",
            path_hint="src/math.py",
            signature="def calculate_sum(a: int, b: int) -> int:",
            doc="Calculates sum of two integers"
        )
        rpg = RPG(nodes=[node], edges=[])
        interfaces = {"src/math.py": "def calculate_sum(a: int, b: int) -> int: pass"}

        impl_code = await generator._generate_implementation(node, interfaces, rpg)

        assert isinstance(impl_code, str)
        assert len(impl_code) > 0


class TestBuildDebugPrompt:
    """Tests for debug prompt building."""

    @pytest.fixture
    def generator(self, sample_project_config, mock_llm_client, mock_docker_runner):
        """Create generator for testing."""
        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    @pytest.mark.asyncio
    async def test_build_debug_prompt(self, generator, simple_rpg):
        """Test debug prompt building."""
        node = RPGNode(
            id="func-1",
            name="test_func",
            kind="function",
            path_hint="src/test.py",
            signature="def test_func():",
            doc="Test function"
        )

        from zerorepo.rpg.graph_ops import RPGGraphOps
        graph_ops = RPGGraphOps(simple_rpg)

        test_result = {
            "success": False,
            "output": "AssertionError: 1 != 2",
            "error": "Tests failed"
        }

        prompt = await generator._build_debug_prompt(
            node,
            "def test_func(): return 1",
            "def test_func(): assert test_func() == 2",
            test_result,
            graph_ops
        )

        assert isinstance(prompt, str)
        assert "test_func" in prompt
        assert "AssertionError" in prompt


class TestCreateDirectoryStructure:
    """Tests for directory structure creation."""

    @pytest.fixture
    def generator(self, sample_project_config, mock_llm_client, mock_docker_runner):
        """Create generator for testing."""
        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    def test_create_directory_structure(self, generator, temp_output_dir):
        """Test directory structure creation."""
        nodes = [
            RPGNode(id="f1", name="src", kind="folder", path_hint="src/"),
            RPGNode(id="f2", name="algorithms", kind="folder", path_hint="src/algorithms/"),
        ]
        rpg = RPG(nodes=nodes, edges=[])

        generator._create_directory_structure(rpg, temp_output_dir)

        assert os.path.exists(os.path.join(temp_output_dir, "src"))
        assert os.path.exists(os.path.join(temp_output_dir, "src", "algorithms"))
        assert os.path.exists(os.path.join(temp_output_dir, "tests"))


class TestWriteFile:
    """Tests for file writing."""

    @pytest.fixture
    def generator(self, sample_project_config, mock_llm_client, mock_docker_runner):
        """Create generator for testing."""
        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    def test_write_file_creates_file(self, generator, temp_output_dir):
        """Test file writing creates file."""
        file_path = os.path.join(temp_output_dir, "test", "module.py")
        content = "# Test module\nprint('hello')"

        generator._write_file(file_path, content)

        assert os.path.exists(file_path)
        with open(file_path) as f:
            assert f.read() == content

    def test_write_file_creates_directories(self, generator, temp_output_dir):
        """Test file writing creates parent directories."""
        file_path = os.path.join(temp_output_dir, "a", "b", "c", "module.py")
        content = "# Nested module"

        generator._write_file(file_path, content)

        assert os.path.exists(file_path)


class TestGetTestFilePath:
    """Tests for test file path generation."""

    @pytest.fixture
    def generator(self, sample_project_config, mock_llm_client, mock_docker_runner):
        """Create generator for testing."""
        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    def test_get_test_path_with_src_prefix(self, generator, temp_output_dir):
        """Test test path generation with src prefix."""
        node = RPGNode(
            id="func-1",
            name="linear",
            kind="function",
            path_hint="src/algorithms/linear.py"
        )

        test_path = generator._get_test_file_path(node, temp_output_dir)

        assert "tests" in test_path
        assert "test_linear.py" in test_path

    def test_get_test_path_without_path_hint(self, generator, temp_output_dir):
        """Test test path generation without path hint."""
        node = RPGNode(
            id="func-1",
            name="MyFunction",
            kind="function"
        )

        test_path = generator._get_test_file_path(node, temp_output_dir)

        assert "tests" in test_path
        assert "myfunction" in test_path.lower()


class TestGetNodeDependencies:
    """Tests for node dependency retrieval."""

    @pytest.fixture
    def generator(self, sample_project_config, mock_llm_client, mock_docker_runner):
        """Create generator for testing."""
        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    def test_get_dependencies_with_edges(self, generator):
        """Test getting dependencies from edges."""
        nodes = [
            RPGNode(id="base", name="BaseClass", kind="class"),
            RPGNode(id="derived", name="DerivedClass", kind="class"),
        ]
        edges = [
            RPGEdge(from_node="base", to_node="derived", type="data_flow")
        ]
        rpg = RPG(nodes=nodes, edges=edges)

        node = nodes[1]
        deps = generator._get_node_dependencies(node, rpg)

        assert isinstance(deps, list)

    def test_get_dependencies_no_edges(self, generator):
        """Test getting dependencies when no edges."""
        nodes = [RPGNode(id="isolated", name="Isolated", kind="function")]
        rpg = RPG(nodes=nodes, edges=[])

        deps = generator._get_node_dependencies(nodes[0], rpg)

        assert deps == []


class TestCalculateTotalLOC:
    """Tests for lines of code calculation."""

    @pytest.fixture
    def generator(self, sample_project_config, mock_llm_client, mock_docker_runner):
        """Create generator for testing."""
        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    def test_calculate_loc_empty_dir(self, generator, temp_output_dir):
        """Test LOC calculation on empty directory."""
        loc = generator._calculate_total_loc(temp_output_dir)

        assert loc == 0

    def test_calculate_loc_with_files(self, generator, temp_output_dir):
        """Test LOC calculation with Python files."""
        # Create some Python files
        os.makedirs(os.path.join(temp_output_dir, "src"))
        with open(os.path.join(temp_output_dir, "src", "module.py"), "w") as f:
            f.write("def hello():\n    return 42\n\n# Comment\n\nprint('test')")

        loc = generator._calculate_total_loc(temp_output_dir)

        # Should count non-empty, non-comment lines
        assert loc > 0


class TestRunIntegrationTests:
    """Tests for integration test running."""

    @pytest.fixture
    def generator(self, sample_project_config, mock_llm_client, mock_docker_runner):
        """Create generator for testing."""
        return CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

    @pytest.mark.asyncio
    async def test_run_integration_tests_no_tests(self, generator, temp_output_dir):
        """Test running integration tests when no tests exist."""
        result = await generator._run_integration_tests(temp_output_dir)

        assert result["integration_tests"] == "no_tests"

    @pytest.mark.asyncio
    async def test_run_integration_tests_success(self, sample_project_config, temp_project_dir):
        """Test running integration tests successfully."""
        mock_llm_client = MagicMock()
        mock_docker_runner = MagicMock()
        mock_docker_runner.run_all_tests = AsyncMock(return_value={
            "success": True,
            "total_tests": 5,
            "passed_tests": 5,
            "failed_tests": 0
        })

        generator = CodeGenerator(
            config=sample_project_config,
            llm_client=mock_llm_client,
            docker_runner=mock_docker_runner
        )

        result = await generator._run_integration_tests(temp_project_dir)

        assert result["integration_tests"] == "passed"
        assert result["passed_tests"] == 5
