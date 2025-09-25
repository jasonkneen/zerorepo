# Planning Controllers

Proposal and implementation planning for the ZeroRepo system.

## 📋 Planning Stages

### Stage A: Proposal Construction (`proposal.py`)
- **Explore-Exploit Strategy** - Balanced feature selection
- **Missing Feature Synthesis** - LLM-generated gap filling
- **Capability Graph Construction** - Hierarchical structure building

### Stage B: Implementation Construction (`implementation.py`)
- **File Structure Encoding** - Capability to file mapping
- **Interface Generation** - Typed interface specifications
- **Data Flow Analysis** - Inter-module dependency mapping

## 🧠 Key Algorithms

### Feature Selection
```python
from zerorepo.plan.proposal import ProposalController

controller = ProposalController(config, llm_client, vector_store)

# Run complete proposal construction
capability_graph, features = await controller.build_capability_graph()
```

### Implementation Design
```python
from zerorepo.plan.implementation import ImplementationController

controller = ImplementationController(config, llm_client)

# Convert capabilities to implementation
complete_graph, interfaces = await controller.build_implementation_graph(capability_graph)
```

## 🔍 Feature Selection Strategies

### Exploit Phase
- Vector similarity search
- High-relevance feature retrieval
- Score-based selection

### Explore Phase  
- Diversity sampling
- Breadth injection
- Coverage optimization

### Missing Phase
- LLM gap analysis
- Hierarchical synthesis
- Completeness validation

## 📊 Quality Control

### Acceptance Filters
- Duplicate avoidance
- Generic infrastructure filtering
- Relevance threshold enforcement
- Similarity-based deduplication

### Validation
- Feature path consistency
- Capability hierarchy integrity
- Interface specification completeness