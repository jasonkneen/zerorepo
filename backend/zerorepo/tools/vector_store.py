"""
Vector Store for feature embeddings using FAISS.
Supports feature search, similarity matching, and diversity sampling.
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Optional, Dict, Tuple
from sentence_transformers import SentenceTransformer
from ..core.models import FeaturePath
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-based vector store for feature path embeddings and retrieval.
    """
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", dimension: int = 384):
        self.embedding_model_name = embedding_model
        self.dimension = dimension
        self.encoder = SentenceTransformer(embedding_model)
        
        # FAISS index
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.feature_paths: List[FeaturePath] = []
        self.embeddings: Optional[np.ndarray] = None
        
        logger.info(f"Vector store initialized with {embedding_model}")
        
    def add_features(self, feature_paths: List[FeaturePath]) -> None:
        """
        Add feature paths to the vector store.
        
        Args:
            feature_paths: List of FeaturePath objects to index
        """
        if not feature_paths:
            return
            
        logger.info(f"Adding {len(feature_paths)} features to vector store")
        
        # Create embeddings
        texts = [self._feature_to_text(fp) for fp in feature_paths]
        embeddings = self.encoder.encode(texts)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings.astype(np.float32))
        
        # Store metadata
        self.feature_paths.extend(feature_paths)
        
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
            
        logger.info(f"Vector store now contains {len(self.feature_paths)} features")
        
    def build_from_ontology(self, ontology_data: Dict) -> None:
        """
        Build vector store from a feature ontology/taxonomy.
        
        Args:
            ontology_data: Hierarchical feature data structure
        """
        logger.info("Building vector store from ontology")
        
        feature_paths = []
        self._extract_paths_from_ontology(ontology_data, "", feature_paths)
        
        # Create FeaturePath objects with base scores
        features = [
            FeaturePath(path=path, score=0.5, source="ontology") 
            for path in feature_paths
        ]
        
        self.add_features(features)
        
    def _extract_paths_from_ontology(self, data: Dict, prefix: str, paths: List[str]) -> None:
        """Recursively extract paths from hierarchical ontology."""
        for key, value in data.items():
            current_path = f"{prefix}/{key}" if prefix else key
            
            if isinstance(value, dict):
                paths.append(current_path)
                self._extract_paths_from_ontology(value, current_path, paths)
            elif isinstance(value, list):
                paths.append(current_path)
                for item in value:
                    paths.append(f"{current_path}/{item}")
            else:
                paths.append(current_path)
                
    async def search_features(
        self,
        query: str,
        k: int = 10,
        domain_filter: Optional[str] = None,
        min_score: float = 0.1
    ) -> List[FeaturePath]:
        """
        Search for similar features using vector similarity.
        
        Args:
            query: Search query text
            k: Number of results to return
            domain_filter: Filter by domain (e.g., 'ml', 'web')
            min_score: Minimum similarity score threshold
            
        Returns:
            List of similar FeaturePath objects with scores
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []
            
        # Encode query
        query_embedding = self.encoder.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype(np.float32), min(k * 2, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.feature_paths) and score >= min_score:
                feature_path = self.feature_paths[idx]
                
                # Apply domain filter
                if domain_filter and not feature_path.path.startswith(domain_filter):
                    continue
                    
                # Create result with updated score
                result = FeaturePath(
                    path=feature_path.path,
                    score=float(score),
                    source="exploit"
                )
                results.append(result)
                
        return results[:k]
        
    async def sample_diverse_features(
        self,
        exclude_paths: set,
        k: int = 10,
        domain_filter: Optional[str] = None,
        diversity_weight: float = 0.5
    ) -> List[FeaturePath]:
        """
        Sample diverse features for exploration.
        
        Args:
            exclude_paths: Paths to exclude from sampling
            k: Number of features to sample
            domain_filter: Filter by domain
            diversity_weight: Weight for diversity vs relevance
            
        Returns:
            List of diverse FeaturePath objects
        """
        if self.index.ntotal == 0:
            return []
            
        # Filter available features
        available_features = [
            fp for fp in self.feature_paths 
            if fp.path not in exclude_paths
        ]
        
        if domain_filter:
            available_features = [
                fp for fp in available_features
                if fp.path.startswith(domain_filter)
            ]
            
        if len(available_features) <= k:
            return available_features
            
        # Use simple random sampling for diversity
        # In production, could implement more sophisticated diversity algorithms
        import random
        sampled = random.sample(available_features, k)
        
        # Update source to explore
        for feature in sampled:
            feature.source = "explore"
            feature.score = 0.6  # Medium confidence for exploration
            
        return sampled
        
    def get_feature_neighborhoods(self, feature_path: str, radius: int = 5) -> List[FeaturePath]:
        """
        Get neighborhood features for a given feature path.
        
        Args:
            feature_path: Target feature path
            radius: Number of neighbors to return
            
        Returns:
            List of neighboring FeaturePath objects
        """
        # Find the target feature
        target_idx = None
        for i, fp in enumerate(self.feature_paths):
            if fp.path == feature_path:
                target_idx = i
                break
                
        if target_idx is None:
            return []
            
        if self.embeddings is None:
            return []
            
        # Get embedding for target
        target_embedding = self.embeddings[target_idx:target_idx+1]
        
        # Search for neighbors
        scores, indices = self.index.search(target_embedding.astype(np.float32), radius + 1)
        
        neighbors = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != target_idx and idx < len(self.feature_paths):
                neighbor = self.feature_paths[idx]
                neighbor.score = float(score)
                neighbors.append(neighbor)
                
        return neighbors
        
    def save(self, filepath: str) -> None:
        """Save vector store to disk."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, f"{filepath}.index")
            
            # Save metadata
            metadata = {
                "feature_paths": self.feature_paths,
                "embeddings": self.embeddings,
                "dimension": self.dimension,
                "model_name": self.embedding_model_name
            }
            
            with open(f"{filepath}.metadata", "wb") as f:
                pickle.dump(metadata, f)
                
            logger.info(f"Vector store saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save vector store: {str(e)}")
            raise
            
    def load(self, filepath: str) -> None:
        """Load vector store from disk."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{filepath}.index")
            
            # Load metadata
            with open(f"{filepath}.metadata", "rb") as f:
                metadata = pickle.load(f)
                
            self.feature_paths = metadata["feature_paths"]
            self.embeddings = metadata["embeddings"]
            self.dimension = metadata["dimension"]
            
            logger.info(f"Vector store loaded from {filepath}")
            logger.info(f"Loaded {len(self.feature_paths)} features")
            
        except Exception as e:
            logger.error(f"Failed to load vector store: {str(e)}")
            raise
            
    def _feature_to_text(self, feature_path: FeaturePath) -> str:
        """Convert FeaturePath to searchable text."""
        # Convert path to natural language
        path_parts = feature_path.path.split('/')
        text_parts = []
        
        for part in path_parts:
            # Convert snake_case to readable text
            readable = part.replace('_', ' ').replace('-', ' ')
            text_parts.append(readable)
            
        # Create searchable text
        text = ' '.join(text_parts)
        
        # Add context based on common patterns
        if 'ml' in path_parts or 'machine' in text.lower():
            text += " machine learning artificial intelligence"
        if 'algorithm' in text.lower():
            text += " computation method implementation"
        if 'data' in text.lower():
            text += " dataset processing analysis"
            
        return text
        
    def get_stats(self) -> Dict[str, int]:
        """Get vector store statistics."""
        return {
            "total_features": len(self.feature_paths),
            "index_size": self.index.ntotal,
            "dimension": self.dimension,
            "sources": {
                "exploit": len([f for f in self.feature_paths if f.source == "exploit"]),
                "explore": len([f for f in self.feature_paths if f.source == "explore"]), 
                "missing": len([f for f in self.feature_paths if f.source == "missing"]),
                "ontology": len([f for f in self.feature_paths if f.source == "ontology"])
            }
        }
        
    def create_sample_ontology(self) -> Dict:
        """Create a sample ML feature ontology for testing."""
        return {
            "ml": {
                "algorithms": {
                    "supervised": {
                        "regression": ["linear", "polynomial", "ridge", "lasso"],
                        "classification": ["logistic", "svm", "naive_bayes", "decision_tree", "random_forest"]
                    },
                    "unsupervised": {
                        "clustering": ["kmeans", "hierarchical", "dbscan"],
                        "dimensionality_reduction": ["pca", "lda", "tsne", "umap"]
                    },
                    "ensemble": ["random_forest", "gradient_boosting", "adaboost"]
                },
                "preprocessing": {
                    "scaling": ["standard_scaler", "min_max_scaler", "robust_scaler"],
                    "encoding": ["one_hot", "label_encoding", "ordinal_encoding"],
                    "feature_selection": ["variance_threshold", "correlation_filter", "mutual_info"]
                },
                "evaluation": {
                    "regression_metrics": ["mse", "mae", "r2_score"],
                    "classification_metrics": ["accuracy", "precision", "recall", "f1_score", "auc_roc"],
                    "clustering_metrics": ["silhouette_score", "calinski_harabasz", "davies_bouldin"]
                },
                "data": {
                    "loading": ["csv_loader", "json_loader", "database_connector"],
                    "splitting": ["train_test_split", "cross_validation", "stratified_split"],
                    "validation": ["data_validator", "schema_checker", "outlier_detector"]
                },
                "optimization": {
                    "gradient_descent": ["sgd", "adam", "rmsprop"],
                    "hyperparameter_tuning": ["grid_search", "random_search", "bayesian_optimization"]
                }
            },
            "data_science": {
                "visualization": ["matplotlib", "seaborn", "plotly"],
                "statistics": ["descriptive", "inferential", "hypothesis_testing"],
                "time_series": ["arima", "seasonal_decomposition", "forecasting"]
            },
            "utils": {
                "io": ["file_handler", "data_serializer"],
                "logging": ["logger_config", "metrics_tracker"],
                "config": ["parameter_manager", "environment_config"]
            }
        }