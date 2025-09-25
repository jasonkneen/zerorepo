# Repository Planning Graph Operations

Graph operations and utilities for Repository Planning Graphs (RPG).

## 🔄 Core Operations

### Graph Validation
- **DAG Validation** - Ensures acyclic structure
- **Connectivity Analysis** - Identifies isolated nodes
- **Reference Validation** - Verifies edge integrity

### Graph Analysis
- **Topological Sorting** - Generation order computation
- **Dependency Analysis** - Multi-level dependency tracking
- **Neighborhood Exploration** - Context analysis for debugging

## 🧮 Key Classes

### RPGGraphOps
```python
from zerorepo.rpg.graph_ops import RPGGraphOps

ops = RPGGraphOps(rpg)

# Validate graph structure
is_valid, errors = ops.validate_dag()

# Get generation order
topo_order = ops.topological_sort()

# Find dependencies
deps = ops.get_dependencies(node_id, max_depth=3)

# Search by functionality
matches = ops.find_by_functionality("regression")
```

## 📈 Metrics

### Graph Metrics
- Node counts by type (capability, file, class, function)
- Edge counts by type (data_flow, depends_on, order)
- Connectivity and structure analysis

### Performance Tracking
- Generation order validation
- Dependency resolution efficiency
- Graph complexity metrics

## 🔬 Research Foundation

Implements graph theory concepts from the Repository Planning Graphs paper:
- Directed Acyclic Graph (DAG) constraints
- Topological ordering for dependency resolution
- Graph-guided debugging and localization