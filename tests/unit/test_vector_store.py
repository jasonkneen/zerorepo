"""
Unit tests for Vector Store.
Tests FAISS indexing, feature search, and embedding operations.
"""

import pytest
from unittest.mock import MagicMock, patch
import tempfile
import os

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

# Check for optional dependencies
try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    np = None

if not DEPS_AVAILABLE:
    pytest.skip("FAISS/numpy/sentence-transformers not installed", allow_module_level=True)

from zerorepo.core.models import FeaturePath


class TestVectorStoreInit:
    """Tests for VectorStore initialization."""

    @patch('zerorepo.tools.vector_store.SentenceTransformer')
    @patch('zerorepo.tools.vector_store.faiss')
    def test_init_default_parameters(self, mock_faiss, mock_st):
        """Test initialization with default parameters."""
        from zerorepo.tools.vector_store import VectorStore

        mock_faiss.IndexFlatIP.return_value = MagicMock()

        store = VectorStore()

        assert store.embedding_model_name == "all-MiniLM-L6-v2"
        assert store.dimension == 384
        mock_st.assert_called_once_with("all-MiniLM-L6-v2")

    @patch('zerorepo.tools.vector_store.SentenceTransformer')
    @patch('zerorepo.tools.vector_store.faiss')
    def test_init_custom_parameters(self, mock_faiss, mock_st):
        """Test initialization with custom parameters."""
        from zerorepo.tools.vector_store import VectorStore

        mock_faiss.IndexFlatIP.return_value = MagicMock()

        store = VectorStore(embedding_model="custom-model", dimension=768)

        assert store.embedding_model_name == "custom-model"
        assert store.dimension == 768


class TestVectorStoreAddFeatures:
    """Tests for adding features to vector store."""

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_encoder.encode.return_value = np.random.rand(1, 384).astype(np.float32)
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 0
            mock_faiss.IndexFlatIP.return_value = mock_index
            mock_faiss.normalize_L2 = MagicMock()

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            return store, mock_encoder, mock_index

    def test_add_empty_features(self, mock_vector_store):
        """Test adding empty feature list."""
        store, mock_encoder, _ = mock_vector_store

        store.add_features([])

        mock_encoder.encode.assert_not_called()

    def test_add_single_feature(self, mock_vector_store):
        """Test adding a single feature."""
        store, mock_encoder, mock_index = mock_vector_store

        feature = FeaturePath(path="ml/algorithms/linear", score=0.9, source="exploit")

        # Set up return value for single item batch
        mock_encoder.encode.return_value = np.random.rand(1, 384).astype(np.float32)

        store.add_features([feature])

        assert len(store.feature_paths) == 1
        assert store.feature_paths[0].path == "ml/algorithms/linear"

    def test_add_multiple_features(self, mock_vector_store):
        """Test adding multiple features."""
        store, mock_encoder, mock_index = mock_vector_store

        features = [
            FeaturePath(path="ml/algorithms/linear", score=0.9, source="exploit"),
            FeaturePath(path="ml/algorithms/logistic", score=0.8, source="explore"),
            FeaturePath(path="ml/preprocessing/scaling", score=0.7, source="missing"),
        ]

        mock_encoder.encode.return_value = np.random.rand(3, 384).astype(np.float32)

        store.add_features(features)

        assert len(store.feature_paths) == 3


class TestVectorStoreBuildFromOntology:
    """Tests for building from ontology."""

    @pytest.fixture
    def mock_store_for_ontology(self):
        """Create mock store for ontology testing."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 0
            mock_faiss.IndexFlatIP.return_value = mock_index
            mock_faiss.normalize_L2 = MagicMock()

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            return store, mock_encoder

    def test_build_from_simple_ontology(self, mock_store_for_ontology, ml_ontology):
        """Test building from simple ML ontology."""
        store, mock_encoder = mock_store_for_ontology

        # Mock encoding to return array matching number of features
        def encode_side_effect(texts, **kwargs):
            return np.random.rand(len(texts), 384).astype(np.float32)

        mock_encoder.encode.side_effect = encode_side_effect

        store.build_from_ontology(ml_ontology)

        # Should have extracted multiple paths
        assert len(store.feature_paths) > 0

    def test_build_from_empty_ontology(self, mock_store_for_ontology):
        """Test building from empty ontology."""
        store, mock_encoder = mock_store_for_ontology

        store.build_from_ontology({})

        assert len(store.feature_paths) == 0


class TestVectorStoreSearch:
    """Tests for feature search functionality."""

    @pytest.fixture
    def populated_mock_store(self):
        """Create populated mock store for search testing."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_encoder.encode.return_value = np.random.rand(1, 384).astype(np.float32)
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 5
            # Return high scores and valid indices
            mock_index.search.return_value = (
                np.array([[0.9, 0.8, 0.7, 0.6, 0.5]]),
                np.array([[0, 1, 2, 3, 4]])
            )
            mock_faiss.IndexFlatIP.return_value = mock_index
            mock_faiss.normalize_L2 = MagicMock()

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            # Pre-populate with features
            store.feature_paths = [
                FeaturePath(path="ml/algorithms/linear", score=0.9, source="exploit"),
                FeaturePath(path="ml/algorithms/logistic", score=0.8, source="exploit"),
                FeaturePath(path="ml/preprocessing/scaling", score=0.7, source="explore"),
                FeaturePath(path="data/loading", score=0.6, source="ontology"),
                FeaturePath(path="utils/config", score=0.5, source="ontology"),
            ]

            return store

    @pytest.mark.asyncio
    async def test_search_empty_store(self):
        """Test searching empty store."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 0
            mock_faiss.IndexFlatIP.return_value = mock_index

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            results = await store.search_features("linear regression", k=5)

            assert results == []

    @pytest.mark.asyncio
    async def test_search_returns_results(self, populated_mock_store):
        """Test search returns matching results."""
        results = await populated_mock_store.search_features("linear regression", k=3)

        assert len(results) <= 3
        for result in results:
            assert isinstance(result, FeaturePath)

    @pytest.mark.asyncio
    async def test_search_with_domain_filter(self, populated_mock_store):
        """Test search with domain filter."""
        results = await populated_mock_store.search_features(
            "algorithms",
            k=5,
            domain_filter="ml"
        )

        for result in results:
            assert result.path.startswith("ml")

    @pytest.mark.asyncio
    async def test_search_with_min_score(self, populated_mock_store):
        """Test search with minimum score threshold."""
        results = await populated_mock_store.search_features(
            "algorithms",
            k=10,
            min_score=0.7
        )

        for result in results:
            assert result.score >= 0.7


class TestVectorStoreDiverseSampling:
    """Tests for diverse feature sampling."""

    @pytest.fixture
    def store_for_sampling(self):
        """Create store for sampling tests."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 10
            mock_faiss.IndexFlatIP.return_value = mock_index

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            # Pre-populate
            store.feature_paths = [
                FeaturePath(path=f"ml/feature{i}", score=0.5, source="ontology")
                for i in range(10)
            ]

            return store

    @pytest.mark.asyncio
    async def test_diverse_sample_empty_store(self):
        """Test diverse sampling on empty store."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 0
            mock_faiss.IndexFlatIP.return_value = mock_index

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            results = await store.sample_diverse_features(exclude_paths=set(), k=5)

            assert results == []

    @pytest.mark.asyncio
    async def test_diverse_sample_with_exclusions(self, store_for_sampling):
        """Test diverse sampling excludes specified paths."""
        exclude = {"ml/feature0", "ml/feature1"}

        results = await store_for_sampling.sample_diverse_features(
            exclude_paths=exclude,
            k=5
        )

        for result in results:
            assert result.path not in exclude

    @pytest.mark.asyncio
    async def test_diverse_sample_respects_k(self, store_for_sampling):
        """Test diverse sampling returns at most k results."""
        results = await store_for_sampling.sample_diverse_features(
            exclude_paths=set(),
            k=3
        )

        assert len(results) <= 3

    @pytest.mark.asyncio
    async def test_diverse_sample_with_domain_filter(self, store_for_sampling):
        """Test diverse sampling with domain filter."""
        results = await store_for_sampling.sample_diverse_features(
            exclude_paths=set(),
            k=5,
            domain_filter="ml"
        )

        for result in results:
            assert result.path.startswith("ml")


class TestVectorStoreNeighborhood:
    """Tests for feature neighborhood retrieval."""

    @pytest.fixture
    def store_with_embeddings(self):
        """Create store with embeddings for neighborhood testing."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 5
            mock_index.search.return_value = (
                np.array([[1.0, 0.9, 0.8, 0.7, 0.6]]),
                np.array([[0, 1, 2, 3, 4]])
            )
            mock_faiss.IndexFlatIP.return_value = mock_index

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            store.feature_paths = [
                FeaturePath(path=f"ml/feature{i}", score=0.5, source="ontology")
                for i in range(5)
            ]
            store.embeddings = np.random.rand(5, 384).astype(np.float32)

            return store

    def test_neighborhood_existing_feature(self, store_with_embeddings):
        """Test getting neighborhood of existing feature."""
        neighbors = store_with_embeddings.get_feature_neighborhoods(
            "ml/feature0",
            radius=3
        )

        assert isinstance(neighbors, list)

    def test_neighborhood_nonexistent_feature(self, store_with_embeddings):
        """Test getting neighborhood of non-existent feature."""
        neighbors = store_with_embeddings.get_feature_neighborhoods(
            "nonexistent/path",
            radius=3
        )

        assert neighbors == []


class TestVectorStorePersistence:
    """Tests for save/load functionality."""

    @pytest.fixture
    def store_for_persistence(self):
        """Create store for persistence testing."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 3
            mock_faiss.IndexFlatIP.return_value = mock_index
            mock_faiss.write_index = MagicMock()
            mock_faiss.read_index = MagicMock(return_value=mock_index)

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            store.feature_paths = [
                FeaturePath(path="ml/feature1", score=0.9, source="exploit"),
                FeaturePath(path="ml/feature2", score=0.8, source="explore"),
            ]
            store.embeddings = np.random.rand(2, 384).astype(np.float32)

            return store, mock_faiss

    def test_save_creates_files(self, store_for_persistence):
        """Test that save creates necessary files."""
        store, mock_faiss = store_for_persistence

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_store")

            store.save(filepath)

            # Should attempt to write index
            mock_faiss.write_index.assert_called_once()
            # Metadata file should exist
            assert os.path.exists(f"{filepath}.metadata")

    def test_load_restores_state(self, store_for_persistence):
        """Test that load restores state."""
        store, mock_faiss = store_for_persistence

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_store")

            # Save first
            store.save(filepath)

            # Create new store and load
            with patch('zerorepo.tools.vector_store.SentenceTransformer'):
                from zerorepo.tools.vector_store import VectorStore
                new_store = VectorStore()
                new_store.load(filepath)

            mock_faiss.read_index.assert_called()


class TestVectorStoreStats:
    """Tests for statistics retrieval."""

    def test_get_stats_empty_store(self):
        """Test statistics on empty store."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 0
            mock_faiss.IndexFlatIP.return_value = mock_index

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            stats = store.get_stats()

            assert stats["total_features"] == 0
            assert stats["index_size"] == 0

    def test_get_stats_populated_store(self):
        """Test statistics on populated store."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_index.ntotal = 10
            mock_faiss.IndexFlatIP.return_value = mock_index

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            store.feature_paths = [
                FeaturePath(path="f1", score=0.9, source="exploit"),
                FeaturePath(path="f2", score=0.8, source="explore"),
                FeaturePath(path="f3", score=0.7, source="missing"),
                FeaturePath(path="f4", score=0.6, source="ontology"),
            ]

            stats = store.get_stats()

            assert stats["total_features"] == 4
            assert stats["sources"]["exploit"] == 1
            assert stats["sources"]["explore"] == 1
            assert stats["sources"]["missing"] == 1
            assert stats["sources"]["ontology"] == 1


class TestVectorStoreOntology:
    """Tests for sample ontology creation."""

    def test_create_sample_ontology(self):
        """Test sample ontology creation."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_faiss.IndexFlatIP.return_value = mock_index

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            ontology = store.create_sample_ontology()

            assert isinstance(ontology, dict)
            assert "ml" in ontology
            assert "algorithms" in ontology["ml"]

    def test_sample_ontology_structure(self):
        """Test sample ontology has expected structure."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_faiss.IndexFlatIP.return_value = mock_index

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            ontology = store.create_sample_ontology()

            # Check ML algorithms structure
            assert "supervised" in ontology["ml"]["algorithms"]
            assert "unsupervised" in ontology["ml"]["algorithms"]

            # Check preprocessing
            assert "preprocessing" in ontology["ml"]

            # Check evaluation
            assert "evaluation" in ontology["ml"]


class TestFeatureToText:
    """Tests for feature path to text conversion."""

    def test_feature_to_text_simple(self):
        """Test simple feature path conversion."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_faiss.IndexFlatIP.return_value = mock_index

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            feature = FeaturePath(path="ml/algorithms", score=0.5, source="ontology")
            text = store._feature_to_text(feature)

            assert "ml" in text
            assert "algorithms" in text

    def test_feature_to_text_adds_context(self):
        """Test that context keywords are added."""
        with patch('zerorepo.tools.vector_store.SentenceTransformer') as mock_st, \
             patch('zerorepo.tools.vector_store.faiss') as mock_faiss:

            mock_encoder = MagicMock()
            mock_st.return_value = mock_encoder

            mock_index = MagicMock()
            mock_faiss.IndexFlatIP.return_value = mock_index

            from zerorepo.tools.vector_store import VectorStore
            store = VectorStore()

            feature = FeaturePath(path="ml/algorithms/linear", score=0.5, source="ontology")
            text = store._feature_to_text(feature)

            # Should add ML-related context
            assert "machine learning" in text.lower() or "ml" in text.lower()
