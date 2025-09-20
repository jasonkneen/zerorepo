# ZeroRepo Tools and Utilities

Essential tools and integrations for the ZeroRepo system.

## 🛠️ Core Tools

### LLM Integration (`llm_client.py`)
- **Multi-Provider Support** - OpenAI, Anthropic, Google, OpenRouter, GitHub
- **Unified Interface** - Consistent API across all providers
- **JSON Mode** - Structured response generation
- **Error Handling** - Robust retry and fallback mechanisms

### Vector Store (`vector_store.py`)
- **FAISS Backend** - High-performance similarity search
- **Semantic Embeddings** - Sentence transformer models
- **Feature Ontology** - Hierarchical feature taxonomy
- **Diversity Sampling** - Exploration and exploitation strategies

### Docker Runtime (`docker_runtime.py`)
- **Isolated Execution** - Sandboxed test environment
- **Resource Management** - Memory and CPU limits
- **Subprocess Fallback** - Works without Docker
- **Test Analytics** - Comprehensive result parsing

## 🤖 LLM Client Usage

```python
from zerorepo.tools.llm_client import LLMClient

client = LLMClient(api_key="sk-...", default_model="gpt-4o-mini")

# Text generation
response = await client.generate(
    prompt="Generate Python function",
    temperature=0.1,
    max_tokens=1000
)

# JSON generation
json_data = await client.generate_json(
    prompt="Generate feature list",
    schema={"type": "object"}
)
```

## 🔍 Vector Store Operations

```python
from zerorepo.tools.vector_store import VectorStore

store = VectorStore(embedding_model="all-MiniLM-L6-v2")

# Build from ontology
store.build_from_ontology(ontology_data)

# Search features
results = await store.search_features(
    query="machine learning regression",
    k=10,
    domain_filter="ml"
)

# Sample diverse features
diverse = await store.sample_diverse_features(
    exclude_paths=existing_features,
    k=5,
    diversity_weight=0.7
)
```

## 🐳 Docker Test Execution

```python
from zerorepo.tools.docker_runtime import DockerTestRunner

runner = DockerTestRunner(base_image="python:3.11-slim")

# Run single test
result = await runner.run_tests(test_file_path)

# Run all tests
integration_result = await runner.run_all_tests(project_dir)
```

## 🔧 Configuration

### Environment Variables
- `EMERGENT_LLM_KEY` - Unified LLM access (development only)
- Custom provider API keys passed from frontend

### Model Configuration
- **Temperature** - Creativity vs consistency control
- **Max Tokens** - Response length limits
- **Retry Logic** - Failure recovery strategies

## 📊 Performance Monitoring

### LLM Metrics
- Token usage tracking
- Response time monitoring
- Success/failure rates
- Cost optimization

### Vector Operations
- Search latency
- Index size and memory usage
- Embedding quality metrics

### Test Execution
- Container startup time
- Test execution duration
- Resource utilization

---

*Tools and utilities powering ZeroRepo's AI capabilities*