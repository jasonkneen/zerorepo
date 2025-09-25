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
- **LLM Integration** - Multi-provider support (OpenAI, Anthropic, Google, OpenRouter, GitHub)
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
- **Landing Page**: Preview demo and feature overview
- **Quick Demo**: Test the system with optimized AI calls (~30 seconds)
- **Full Generation**: Complete repository generation with live progress tracking

### API Endpoints

```bash
# Quick demo
curl -X POST "/api/zerorepo/quick-demo"

# Plan repository (Stage A)
curl -X POST "/api/zerorepo/plan" \
  -H "Content-Type: application/json" \
  -d '{"project_goal": "Generate ML toolkit", "domain": "ml", "llm_provider": "openai", "api_key": "sk-..."}'

# Generate repository (Full pipeline)
curl -X POST "/api/zerorepo/generate" \
  -H "Content-Type: application/json" \
  -d '{"project_goal": "Generate web app", "domain": "web", "llm_provider": "openai", "api_key": "sk-..."}'

# Check job status
curl "/api/zerorepo/jobs/{job_id}"

# Get available models
curl "/api/models"
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

### LLM Providers
- **OpenAI** - GPT-4o, GPT-4o Mini, GPT-4, GPT-3.5 Turbo
- **Anthropic** - Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
- **Google** - Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash
- **OpenRouter** - Multi-provider access with additional models
- **GitHub Models** - GitHub's AI model marketplace

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
- **EmergentIntegrations** - Multi-provider LLM access
- **Docker** - Isolated test execution

### Frontend
- **React** - Interactive web interface with routing
- **Tailwind CSS** - Modern responsive design with dark mode
- **Lucide Icons** - Professional iconography
- **Axios** - API communication
- **LocalStorage** - Secure client-side API key storage

### Key Dependencies
- `sentence-transformers` - Feature embedding generation
- `pydantic` - Data validation and serialization
- `typer` - CLI interface framework
- `gitpython` - Repository management
- `pyyaml` - Configuration and prompt templates
- `emergentintegrations` - Unified LLM access

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

ZeroRepo implements concepts from ["Repository Planning Graphs for Agentic Software Development"](https://arxiv.org/abs/2509.16198), including:
- Graph-driven repository planning
- Explore-exploit feature selection strategies
- Topological code generation
- Test-driven validation loops
- Graph-guided localization and editing

## 🔑 API Key Requirements

**Production Deployment**: Requires user-provided API keys for LLM providers.
- API keys are stored securely in browser localStorage
- Keys are never transmitted to ZeroRepo servers
- Direct communication with AI providers for privacy and security

**Supported Providers**:
- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [Anthropic API Keys](https://console.anthropic.com/)
- [Google/Gemini API Keys](https://aistudio.google.com/app/apikey)
- [OpenRouter API Keys](https://openrouter.ai/keys)
- [GitHub Models](https://github.com/marketplace/models)

## 🚀 Getting Started

1. **Quick Test**: Use the landing page Quick Demo to verify system functionality
2. **Configure APIs**: Add your API keys in the settings panel
3. **Plan Repository**: Use the planning feature to see AI-generated structure
4. **Generate Code**: Full pipeline with live progress tracking

## 🤝 Contributing

The system is built with extensibility in mind:
- **Domain Ontologies**: Add new feature taxonomies
- **LLM Providers**: Extend the multi-provider interface  
- **Code Generators**: Implement language-specific generators
- **Evaluation Metrics**: Add custom assessment criteria

## 📄 License

MIT License - see LICENSE file for details.

---

*ZeroRepo v1.0 - Built with the Emergent platform*
*Based on "Repository Planning Graphs for Agentic Software Development" - [arXiv:2509.16198](https://arxiv.org/abs/2509.16198)*