# ZeroRepo Core System

The core implementation of the ZeroRepo graph-driven repository generation system.

## 📁 Directory Structure

```
zerorepo/
├── __init__.py           # Package initialization
├── core/                 # Core data models and types
├── rpg/                  # Repository Planning Graph operations
├── plan/                 # Proposal and implementation planning
├── codegen/              # Code generation with test-driven development
├── tools/                # Utilities and integrations
├── cli/                  # Command-line interface
├── prompts/              # LLM prompt templates
└── eval/                 # Evaluation harness
```

## 🧠 Core Concepts

### Repository Planning Graph (RPG)
- **Nodes**: Capabilities, folders, files, classes, functions
- **Edges**: Data flows, dependencies, execution order
- **Validation**: DAG constraints and connectivity requirements

### Three-Stage Pipeline
1. **Proposal Construction** - Feature discovery using explore/exploit/missing
2. **Implementation Design** - File structure and interface generation  
3. **Code Generation** - Topological traversal with test-driven development

## 🔧 Key Classes

### Core Models (`core/models.py`)
- `RPGNode` - Graph node representation
- `RPGEdge` - Graph edge with typed relationships
- `RPG` - Complete graph with validation methods
- `ProjectConfig` - Generation configuration
- `GenerationResult` - Output with metrics

### Graph Operations (`rpg/graph_ops.py`)
- `RPGGraphOps` - NetworkX-based graph analysis
- DAG validation and cycle detection
- Topological sorting for generation order
- Neighborhood analysis for debugging

### Planning Controllers (`plan/`)
- `ProposalController` - Feature selection and capability graph construction
- `ImplementationController` - File structure and interface design

### Code Generation (`codegen/`)
- `CodeGenerator` - Topological code generation with TDD
- Test generation from specifications
- Iterative improvement with AI debugging

### Tools (`tools/`)
- `LLMClient` - Multi-provider LLM integration
- `VectorStore` - FAISS-based semantic search
- `DockerTestRunner` - Isolated test execution

## 🚀 Usage Examples

### Programmatic Usage
```python
from zerorepo.orchestrator import generate_repository

result = await generate_repository(
    project_goal="Generate ML toolkit",
    output_dir="./ml_toolkit",
    domain="ml",
    llm_model="gpt-4o-mini"
)
```

### CLI Usage
```bash
# Plan repository
python zerorepo_cli.py plan --goal "Generate ML toolkit"

# Generate code
python zerorepo_cli.py generate --goal "Build web app"
```

## 🔬 Research Implementation

Implements concepts from [arXiv:2509.16198](https://arxiv.org/abs/2509.16198):

- **Graph-driven planning** with capability decomposition
- **Explore-exploit-missing** feature selection strategies  
- **Topological code generation** with dependency ordering
- **Test-driven validation** with iterative improvement
- **Graph-guided debugging** with contextual error localization

## 🧪 Testing and Debugging

### Debug Scripts
- `debug_pipeline.py` - Test full pipeline stages
- `debug_features.py` - Analyze feature selection process
- `test_real_llm.py` - Verify LLM integration

### Evaluation
- Comprehensive metrics tracking
- RepoCraft-style evaluation harness
- Coverage, novelty, and pass rate analysis

---

*Core implementation of the ZeroRepo system*