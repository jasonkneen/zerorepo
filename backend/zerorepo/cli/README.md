# ZeroRepo CLI Interface

Command-line interface for the ZeroRepo graph-driven repository generation system.

## 🖥️ Available Commands

### Core Commands
```bash
# Plan repository (Stage A only)
zerorepo plan --goal "Generate ML toolkit" --domain ml

# Build from existing RPG
zerorepo build --rpg output/rpg_full.json --output ./generated_repo

# Full pipeline (Plan + Build)
zerorepo generate --goal "Build web app" --domain web

# Initialize new project
zerorepo init my-project --template ml

# Evaluate on benchmark
zerorepo eval --benchmark ./benchmark_tasks --output ./results
```

## 🔧 Usage Examples

### Quick Start
```bash
# Initialize a new ML project
python zerorepo_cli.py init ml-toolkit --template ml

# Generate the repository
python zerorepo_cli.py generate \
  --goal "Generate classical ML algorithms" \
  --domain ml \
  --output ./ml-toolkit

# Evaluate results
python zerorepo_cli.py eval --benchmark ./test_cases
```

### Advanced Usage
```bash
# Plan with custom config
python zerorepo_cli.py plan \
  --goal "Build distributed system" \
  --domain general \
  --model gpt-4o \
  --iterations 5 \
  --config custom_config.json

# Build with specific RPG
python zerorepo_cli.py build \
  --rpg complex_system.json \
  --output ./distributed_system \
  --config production.json
```

## ⚙️ Configuration

### Config File Format (JSON)
```json
{
  "project_goal": "Generate ML toolkit",
  "domain": "ml",
  "target_language": "python",
  "test_framework": "pytest",
  "llm_model": "gpt-4o-mini",
  "max_iterations": 30,
  "max_retries": 8
}
```

### Environment Variables
- API keys must be set in environment or passed via config
- No default Emergent key in production

## 📊 Output

### Generated Artifacts
- **RPG Files** - JSON representation of repository graph
- **Feature Lists** - JSONL format feature paths
- **Generated Code** - Complete Python repository
- **Test Reports** - Comprehensive test results
- **Metrics** - Generation statistics and quality metrics

## 🚀 Integration

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Generate Repository
  run: |
    python zerorepo_cli.py generate \
      --goal "${{ inputs.project_goal }}" \
      --domain "${{ inputs.domain }}" \
      --output ./generated_repo
```

### Batch Processing
```bash
# Process multiple projects
for goal in "ML toolkit" "Web API" "Data pipeline"; do
  python zerorepo_cli.py generate --goal "$goal" --output "./${goal// /_}"
done
```

---

*Command-line interface for professional ZeroRepo usage*