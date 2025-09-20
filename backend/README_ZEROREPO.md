# ZeroRepo: Graph-Driven Repository Generation System

ZeroRepo is a sophisticated agentic system that plans software repositories as Repository Planning Graphs (RPG), refines them into file/data-flow/function designs, and generates code topologically with test-driven validation and graph-guided localization & editing.

## 🚀 Features

### Three-Stage Pipeline
- **Stage A: Proposal Construction** - Capability graphs using explore/exploit/missing feature strategies
- **Stage B: Implementation Design** - File structure encoding and interface specifications  
- **Stage C: Code Generation** - Topological traversal with test-driven development

### Key Components
- **RPG Data Models** - Pydantic-based graph representations with validation
- **Vector Store** - FAISS-powered semantic feature search and ontology management
- **LLM Integration** - Unified client supporting OpenAI, Anthropic, and Google via Emergent key
- **Graph Operations** - NetworkX-based DAG validation and topological sorting
- **Docker Runtime** - Isolated test execution environment
- **CLI Interface** - Comprehensive command-line tool with Typer
- **Web Interface** - React-based UI for interactive repository generation

## 🏗️ Architecture

```
ZeroRepo System
├── Stage A: Proposal Construction
│   ├── Vector retrieval (exploit features)
│   ├── Diversity sampling (explore features) 
│   └── Gap synthesis (missing features)
├── Stage B: Implementation Construction
│   ├── File structure mapping
│   ├── Interface generation
│   └── Data flow encoding
└── Stage C: Code Generation
    ├── Topological traversal
    ├── Test-driven development
    └── Graph-guided debugging
```

## 🖥️ Usage

### Web Interface
Visit the deployed application to use the interactive interface:
- **Quick Demo**: Test the system with a simple ML example
- **Plan Repository**: Generate RPG for your project (Stage A only)
- **Generate Repository**: Full pipeline with code generation

### API Endpoints

```bash
# Quick demo
curl -X POST "/api/zerorepo/quick-demo"

# Plan repository (Stage A)
curl -X POST "/api/zerorepo/plan" \
  -H "Content-Type: application/json" \
  -d '{"project_goal": "Generate ML toolkit", "domain": "ml"}'

# Generate repository (Full pipeline)
curl -X POST "/api/zerorepo/generate" \
  -H "Content-Type: application/json" \
  -d '{"project_goal": "Generate web app", "domain": "web"}'

# Check job status
curl "/api/zerorepo/jobs/{job_id}"
```

### CLI Commands

```bash
# Plan repository
python zerorepo_cli.py plan --goal "Generate ML toolkit" --domain ml

# Build from existing RPG
python zerorepo_cli.py build --rpg rpg_full.json --output ./generated_repo

# Full pipeline
python zerorepo_cli.py generate --goal "Build web app" --domain web

# Initialize project
python zerorepo_cli.py init my-project --template ml
```

## 📊 System Capabilities

### Supported Domains
- **Machine Learning** - Algorithms, preprocessing, evaluation, optimization
- **Web Development** - Frameworks, APIs, frontend components
- **Data Processing** - ETL pipelines, analysis, validation
- **General** - Cross-domain software components

### Generation Features
- **Semantic Feature Search** - Vector-based similarity matching
- **Hierarchical Planning** - Multi-level capability decomposition
- **Interface-Driven Design** - Type-safe code generation
- **Test Validation** - Automated unit test creation and execution
- **Graph-Guided Debugging** - Context-aware error localization

## 🔧 Technical Stack

### Backend
- **FastAPI** - REST API and background job processing
- **PyTorch & FAISS** - Vector embeddings and similarity search
- **NetworkX** - Graph analysis and topological sorting
- **MongoDB** - Job storage and metadata persistence
- **Docker** - Isolated test execution
- **Emergent LLM** - Unified access to multiple LLM providers

### Frontend
- **React** - Interactive web interface
- **Tailwind CSS** - Modern responsive design
- **Axios** - API communication

### Key Dependencies
- `sentence-transformers` - Feature embedding generation
- `pydantic` - Data validation and serialization
- `typer` - CLI interface framework
- `gitpython` - Repository management
- `pyyaml` - Configuration and prompt templates

## 🎯 Example Workflows

### Machine Learning Toolkit
1. **Input**: "Generate a classical ML toolkit with regression, classification, clustering"
2. **Stage A**: Identifies 50+ ML features (algorithms, metrics, preprocessing)
3. **Stage B**: Creates organized file structure (src/algorithms/, src/evaluation/, etc.)
4. **Stage C**: Generates tested implementations with base classes and interfaces

### Web Application
1. **Input**: "Build a REST API with authentication and database models"
2. **Stage A**: Plans API endpoints, auth flows, data models
3. **Stage B**: Designs modular architecture with clear interfaces
4. **Stage C**: Generates FastAPI code with tests and documentation

## 📈 Performance Metrics

The system tracks comprehensive metrics throughout generation:
- **Coverage**: Functional categories implemented
- **Novelty**: Features beyond reference taxonomy
- **Pass Rate**: Generated tests that execute successfully
- **Success Rate**: Overall generation completion rate
- **Scale**: Files, lines of code, and complexity metrics

## 🔬 Research Foundation

ZeroRepo implements concepts from "Repository Planning Graphs for Agentic Software Development", including:
- Graph-driven repository planning
- Explore-exploit feature selection strategies
- Topological code generation
- Test-driven validation loops
- Graph-guided localization and editing

## 🚀 Getting Started

1. **Quick Test**: Use the web interface Quick Demo to verify system functionality
2. **API Integration**: Call the REST endpoints for programmatic access
3. **CLI Usage**: Use the command-line interface for batch processing
4. **Custom Development**: Extend the system with domain-specific ontologies

The ZeroRepo system is designed to scale from simple prototypes to complex software repositories, making it a powerful tool for AI-assisted software development.

## 🤝 Contributing

The system is built with extensibility in mind:
- **Domain Ontologies**: Add new feature taxonomies
- **LLM Providers**: Extend the unified client interface  
- **Code Generators**: Implement language-specific generators
- **Evaluation Metrics**: Add custom assessment criteria

## LICENSE

GNU GENERAL PUBLIC LICENSE
---

*ZeroRepo v1.0 - Built with the Emergent platform*
