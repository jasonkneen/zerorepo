# ZeroRepo Backend

FastAPI-based backend for the ZeroRepo graph-driven repository generation system.

## 🏗️ Architecture

### Core Components

- **`server.py`** - Main FastAPI application with all API endpoints
- **`zerorepo/`** - Core ZeroRepo system implementation
- **`requirements.txt`** - Python dependencies
- **`.env`** - Environment configuration

### API Endpoints

#### Core ZeroRepo
- `POST /api/zerorepo/plan` - Plan repository (Stage A only)
- `POST /api/zerorepo/generate` - Full repository generation
- `POST /api/zerorepo/quick-demo` - Optimized demo (30 seconds)
- `GET /api/zerorepo/jobs/{id}` - Job status and progress
- `GET /api/zerorepo/jobs` - List all jobs
- `GET /api/models` - Available LLM models by provider

#### Utility
- `GET /api/` - Service status
- `GET /api/health` - Health check

## 🔧 Setup

### Installation
```bash
cd backend
pip install -r requirements.txt
```

### Environment Variables
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="zerorepo_db"
CORS_ORIGINS="*"
```

### Running
```bash
# Development
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Production (via supervisor)
sudo supervisorctl restart backend
```

## 🧠 LLM Integration

### Supported Providers
- **OpenAI** - GPT-4o, GPT-4o Mini, GPT-4, GPT-3.5 Turbo
- **Anthropic** - Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
- **Google** - Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash
- **OpenRouter** - Multi-provider access with additional models
- **GitHub Models** - GitHub's AI model marketplace

### Security
- API keys are passed from frontend (localStorage)
- Keys are never stored on server
- Direct communication with AI providers

## 📊 Performance

### Optimization Features
- Configurable iteration limits
- Model selection by speed/quality tradeoffs
- Background job processing
- Progress tracking with granular updates

### Monitoring
- Comprehensive logging
- Job status tracking
- Generation metrics
- Error handling and recovery

## 🔬 Research Implementation

Based on ["Repository Planning Graphs for Agentic Software Development"](https://arxiv.org/abs/2509.16198).

### Three-Stage Pipeline
1. **Proposal Construction** - Feature discovery and selection
2. **Implementation Design** - Architecture and interface design
3. **Code Generation** - Topological code generation with TDD

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Debug individual stages
python debug_pipeline.py
python debug_features.py

# Test LLM integration
python test_real_llm.py
```

## 📂 Directory Structure

```
backend/
├── server.py              # Main FastAPI application
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
├── zerorepo/              # Core system
│   ├── core/             # Data models and types
│   ├── rpg/              # Graph operations
│   ├── plan/             # Proposal and implementation planning
│   ├── codegen/          # Code generation with TDD
│   ├── tools/            # Utilities (LLM, vector store, Docker)
│   ├── cli/              # Command-line interface
│   └── prompts/          # LLM prompt templates
├── debug_*.py            # Debug and testing scripts
└── zerorepo_cli.py       # CLI entry point
```