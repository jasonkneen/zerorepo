# ZeroRepo Tests

Test suite for the ZeroRepo graph-driven repository generation system.

## 🧪 Test Categories

### Unit Tests
- **Core Models** - Pydantic model validation and serialization
- **Graph Operations** - RPG construction and analysis
- **Planning Controllers** - Feature selection and implementation design
- **Code Generation** - TDD cycle and file creation
- **Tools** - LLM client, vector store, Docker runner

### Integration Tests
- **API Endpoints** - FastAPI route testing
- **Pipeline Tests** - End-to-end generation workflows
- **Database Tests** - MongoDB job storage and retrieval
- **LLM Integration** - Multi-provider AI communication

### System Tests
- **Performance Tests** - Generation speed and resource usage
- **Scalability Tests** - Large repository generation
- **Reliability Tests** - Error handling and recovery
- **Security Tests** - API key handling and data privacy

## 🏗️ Test Structure

```
tests/
├── unit/
│   ├── test_core_models.py
│   ├── test_graph_ops.py
│   ├── test_proposal.py
│   └── test_codegen.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_pipeline.py
│   └── test_llm_integration.py
├── system/
│   ├── test_performance.py
│   └── test_reliability.py
└── fixtures/
    ├── sample_rpgs.json
    └── test_configurations.py
```

## 🚀 Running Tests

### Full Test Suite
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=zerorepo --cov-report=html

# Run specific category
pytest tests/unit/
pytest tests/integration/
```

### Individual Tests
```bash
# Test specific component
pytest tests/unit/test_core_models.py

# Test with verbose output
pytest tests/integration/test_api_endpoints.py -v

# Test with specific markers
pytest tests/ -m "slow"
```

## 📋 Test Requirements

### Non-Negotiable Tests
- **`test_rpg_dag.py`** - Every RPG must be a valid DAG
- **`test_interfaces_docstrings.py`** - All interfaces need typed signatures and docs
- **`test_codegen_cycle.py`** - Topological order consistency
- **`test_localization_tools.py`** - Graph-guided search functionality

### Quality Gates
- **90% Test Coverage** - Minimum coverage requirement
- **Zero Critical Issues** - No high-severity failures
- **Performance Benchmarks** - Generation time thresholds
- **Memory Usage** - Resource consumption limits

## 🔧 Test Configuration

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    system: marks tests as system-level tests
```

### Mock Configuration
- **LLM Mocking** - Consistent test responses
- **Database Mocking** - In-memory test databases
- **Docker Mocking** - Subprocess-based test execution
- **File System Mocking** - Temporary directory usage

## 📊 Test Metrics

### Coverage Tracking
- **Line Coverage** - Code execution measurement
- **Branch Coverage** - Decision path testing
- **Function Coverage** - API endpoint testing
- **Integration Coverage** - End-to-end workflow testing

### Performance Benchmarks
- **Generation Speed** - Repository creation time
- **Memory Usage** - Peak memory consumption  
- **API Response Time** - Endpoint latency
- **Database Performance** - Query execution time

## 🚨 Continuous Integration

### GitHub Actions
```yaml
name: ZeroRepo Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=zerorepo
```

---

*Comprehensive testing for reliable repository generation*