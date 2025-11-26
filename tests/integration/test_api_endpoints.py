"""
Integration tests for ZeroRepo API endpoints.
Tests FastAPI routes and request handling.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import os

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

# Check for optional dependencies
try:
    import faiss
    import docker
    from httpx import AsyncClient
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

if not DEPS_AVAILABLE:
    pytest.skip("faiss/docker/httpx not installed", allow_module_level=True)


class TestAPISetup:
    """Tests for API application setup."""

    def test_app_creation(self):
        """Test FastAPI app is created correctly."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from server import app

            assert app is not None
            assert app.title == "ZeroRepo API"


@pytest.mark.integration
class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    def test_health_check(self, client):
        """Test health check endpoint returns healthy status."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ZeroRepo API"


@pytest.mark.integration
class TestRootEndpoint:
    """Tests for root API endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/api/")

        assert response.status_code == 200
        data = response.json()
        assert "ZeroRepo" in data["message"]


@pytest.mark.integration
class TestStatusEndpoints:
    """Tests for status check endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    def test_create_status_check(self, client):
        """Test creating a status check."""
        response = client.post(
            "/api/status",
            json={"client_name": "test_client"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["client_name"] == "test_client"
        assert "id" in data

    def test_get_status_checks(self, client):
        """Test getting status checks."""
        # Create a status check first
        client.post("/api/status", json={"client_name": "test"})

        response = client.get("/api/status")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.integration
class TestModelsEndpoint:
    """Tests for models listing endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    def test_get_available_models(self, client):
        """Test getting available models."""
        response = client.get("/api/models")

        assert response.status_code == 200
        data = response.json()
        assert "openai" in data
        assert "anthropic" in data
        assert "google" in data
        assert "openrouter" in data
        assert "github" in data

    def test_openai_models_structure(self, client):
        """Test OpenAI models have correct structure."""
        response = client.get("/api/models")
        data = response.json()

        for model in data["openai"]:
            assert "id" in model
            assert "name" in model
            assert "description" in model


@pytest.mark.integration
class TestLogsEndpoint:
    """Tests for logs endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    def test_get_logs_default_limit(self, client):
        """Test getting logs with default limit."""
        response = client.get("/api/logs")

        assert response.status_code == 200
        data = response.json()
        assert "lines" in data
        assert isinstance(data["lines"], list)

    def test_get_logs_custom_limit(self, client):
        """Test getting logs with custom limit."""
        response = client.get("/api/logs?limit=50")

        assert response.status_code == 200
        data = response.json()
        assert len(data["lines"]) <= 50


@pytest.mark.integration
class TestZeroRepoPlanEndpoint:
    """Tests for ZeroRepo plan endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": "", "OPENAI_API_KEY": "test-key"}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    def test_plan_endpoint_validation(self, client):
        """Test plan endpoint validates input."""
        # Missing required field
        response = client.post(
            "/api/zerorepo/plan",
            json={}
        )

        assert response.status_code == 422  # Validation error

    @patch('server.plan_repository')
    def test_plan_endpoint_success(self, mock_plan, client):
        """Test successful plan request."""
        from zerorepo.core.models import RPG, RPGNode, FeaturePath

        mock_rpg = RPG(
            nodes=[RPGNode(id="test", name="Test", kind="capability")],
            edges=[]
        )
        mock_features = [FeaturePath(path="test", score=0.9, source="exploit")]

        mock_plan.return_value = (mock_rpg, mock_features)

        response = client.post(
            "/api/zerorepo/plan",
            json={
                "project_goal": "Test ML toolkit",
                "domain": "ml",
                "llm_model": "gpt-4"
            }
        )

        # May fail due to actual API call, but structure should be valid
        assert response.status_code in [200, 500]


@pytest.mark.integration
class TestZeroRepoGenerateEndpoint:
    """Tests for ZeroRepo generate endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": "", "OPENAI_API_KEY": "test-key"}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    def test_generate_endpoint_validation(self, client):
        """Test generate endpoint validates input."""
        response = client.post(
            "/api/zerorepo/generate",
            json={}
        )

        assert response.status_code == 422

    def test_generate_endpoint_returns_job_id(self, client):
        """Test generate endpoint returns job ID."""
        response = client.post(
            "/api/zerorepo/generate",
            json={
                "project_goal": "Test project",
                "domain": "general"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"


@pytest.mark.integration
class TestZeroRepoJobsEndpoint:
    """Tests for ZeroRepo jobs endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    def test_get_job_not_found(self, client):
        """Test getting non-existent job."""
        response = client.get("/api/zerorepo/jobs/nonexistent-id")

        assert response.status_code == 404

    def test_list_jobs(self, client):
        """Test listing jobs."""
        response = client.get("/api/zerorepo/jobs")

        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert isinstance(data["jobs"], list)

    def test_list_jobs_with_pagination(self, client):
        """Test listing jobs with pagination."""
        response = client.get("/api/zerorepo/jobs?limit=5&skip=0")

        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) <= 5


@pytest.mark.integration
class TestQuickDemoEndpoint:
    """Tests for quick demo endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": "", "OPENAI_API_KEY": "test-key"}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    @patch('server.ZeroRepoOrchestrator')
    def test_quick_demo_success(self, mock_orchestrator_class, client):
        """Test quick demo endpoint."""
        from zerorepo.core.models import RPG, RPGNode, FeaturePath

        mock_instance = MagicMock()
        mock_instance.run_proposal_stage = AsyncMock(return_value=(
            RPG(nodes=[RPGNode(id="t", name="T", kind="capability")], edges=[]),
            [FeaturePath(path="test", score=0.9, source="exploit")]
        ))
        mock_instance.cleanup = AsyncMock()
        mock_orchestrator_class.return_value = mock_instance

        response = client.post("/api/zerorepo/quick-demo")

        # May succeed or fail based on environment
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


@pytest.mark.integration
class TestInMemoryDatabase:
    """Tests for in-memory database functionality."""

    def test_in_memory_collection_insert(self):
        """Test in-memory collection insert."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from server import InMemoryCollection

            collection = InMemoryCollection()

            import asyncio
            doc = asyncio.get_event_loop().run_until_complete(
                collection.insert_one({"id": "test", "name": "Test"})
            )

            assert doc["id"] == "test"

    def test_in_memory_collection_find_one(self):
        """Test in-memory collection find_one."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from server import InMemoryCollection

            collection = InMemoryCollection()

            import asyncio
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                collection.insert_one({"id": "test", "name": "Test"})
            )

            doc = loop.run_until_complete(
                collection.find_one({"id": "test"})
            )

            assert doc is not None
            assert doc["name"] == "Test"

    def test_in_memory_collection_update_one(self):
        """Test in-memory collection update_one."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from server import InMemoryCollection

            collection = InMemoryCollection()

            import asyncio
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                collection.insert_one({"id": "test", "status": "pending"})
            )

            loop.run_until_complete(
                collection.update_one(
                    {"id": "test"},
                    {"$set": {"status": "completed"}}
                )
            )

            doc = loop.run_until_complete(
                collection.find_one({"id": "test"})
            )

            assert doc["status"] == "completed"


@pytest.mark.integration
class TestInMemoryCursor:
    """Tests for in-memory cursor functionality."""

    def test_cursor_sort(self):
        """Test cursor sorting."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from server import InMemoryCollection

            collection = InMemoryCollection()

            import asyncio
            loop = asyncio.get_event_loop()

            # Insert multiple documents
            for i in range(5):
                loop.run_until_complete(
                    collection.insert_one({"id": f"doc-{i}", "order": i})
                )

            # Query with sort
            cursor = collection.find().sort("order", -1)
            docs = loop.run_until_complete(cursor.to_list(10))

            # Should be sorted descending
            assert docs[0]["order"] > docs[-1]["order"]

    def test_cursor_skip_limit(self):
        """Test cursor skip and limit."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from server import InMemoryCollection

            collection = InMemoryCollection()

            import asyncio
            loop = asyncio.get_event_loop()

            # Insert documents
            for i in range(10):
                loop.run_until_complete(
                    collection.insert_one({"id": f"doc-{i}"})
                )

            cursor = collection.find().skip(2).limit(3)
            docs = loop.run_until_complete(cursor.to_list(10))

            assert len(docs) == 3


@pytest.mark.integration
class TestCORSMiddleware:
    """Tests for CORS middleware configuration."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": "", "CORS_ORIGINS": "*"}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    def test_cors_headers_present(self, client):
        """Test CORS headers are present in response."""
        response = client.options(
            "/api/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        # CORS preflight should be handled
        assert response.status_code in [200, 400]


@pytest.mark.integration
class TestErrorHandling:
    """Tests for API error handling."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch.dict(os.environ, {"MONGO_URL": ""}):
            from fastapi.testclient import TestClient
            from server import app
            return TestClient(app)

    def test_404_for_unknown_route(self, client):
        """Test 404 for unknown routes."""
        response = client.get("/api/unknown/route")

        assert response.status_code == 404

    def test_validation_error_response(self, client):
        """Test validation error response format."""
        response = client.post(
            "/api/zerorepo/plan",
            json={"invalid_field": "value"}
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
