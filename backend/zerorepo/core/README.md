# ZeroRepo Core Models

Core data models and types for the ZeroRepo system.

## 📊 Data Models

### RPG Components
- **`RPGNode`** - Graph nodes (capabilities, folders, files, classes, functions)
- **`RPGEdge`** - Typed relationships (data_flow, depends_on, order)
- **`RPG`** - Complete graph with validation and query methods

### Feature Management
- **`FeaturePath`** - Hierarchical feature representation
- **`FileSkeleton`** - File system structure mapping
- **`Interface`** - Code interface specifications

### Configuration
- **`ProjectConfig`** - Generation parameters and LLM settings
- **`GenerationResult`** - Output metrics and file tracking

## 🔧 Usage

```python
from zerorepo.core.models import RPG, RPGNode, ProjectConfig

# Create project configuration
config = ProjectConfig(
    project_goal="Generate ML toolkit",
    domain="ml",
    llm_model="gpt-4o-mini"
)

# Work with RPG
rpg = RPG(nodes=[], edges=[])
node = RPGNode(name="LinearRegression", kind="class")
rpg.nodes.append(node)
```

All models use Pydantic for validation and serialization.