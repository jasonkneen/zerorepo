# ZeroRepo Evaluation Harness

Evaluation system for ZeroRepo repository generation quality and performance.

## 📊 Evaluation Metrics

### RepoCraft-Style Metrics
- **Coverage** - Functional categories implemented
- **Novelty** - Features beyond reference taxonomy  
- **Pass Rate** - Generated tests that execute successfully
- **Voting Rate** - Semantic validation success
- **Scale** - Files, LOC, and complexity metrics

### Quality Assessment
- **Functional Correctness** - Generated code execution
- **Test Quality** - Comprehensive test coverage
- **Architecture Quality** - Design pattern adherence
- **Documentation Quality** - Code comments and docstrings

## 🎯 Benchmark Tasks

### Evaluation Categories
- **Algorithm Implementation** - Core CS algorithms
- **Data Structure Implementation** - Lists, trees, graphs
- **ML Pipeline Components** - Feature processing, model training
- **Web Service Components** - APIs, authentication, data models

### Task Format
```json
{
  "task_id": "linear_regression_001",
  "description": "Implement linear regression with gradient descent",
  "domain": "ml",
  "expected_files": ["src/regression.py", "tests/test_regression.py"],
  "validation_tests": "path/to/ground_truth_tests.py",
  "complexity": "medium"
}
```

## 🔬 Evaluation Process

### Offline Benchmark Mode
1. **Task Ingestion** - Load benchmark task specifications
2. **Repository Generation** - Run ZeroRepo on each task
3. **Validation** - Execute ground truth tests
4. **Metrics Collection** - Aggregate quality measurements
5. **Report Generation** - Comprehensive analysis report

### Online Evaluation
- **Real-time Metrics** - Track generation quality during production use
- **User Feedback** - Collect user satisfaction and success rates
- **Performance Monitoring** - Generation time and resource usage

## 📈 Reporting

### HTML Reports
- **Executive Summary** - High-level metrics and trends
- **Detailed Analysis** - Per-task breakdown and insights
- **Comparison Charts** - Performance across domains and complexity levels
- **Recommendations** - Areas for improvement and optimization

### JSON Output
```json
{
  "overall_metrics": {
    "coverage": 0.85,
    "novelty": 0.72,
    "pass_rate": 0.91,
    "voting_rate": 0.88
  },
  "domain_breakdown": {...},
  "scaling_analysis": {...}
}
```

## 🧪 Running Evaluations

### Command Line
```bash
# Run full benchmark
zerorepo eval --benchmark ./benchmark_suite --output ./results

# Domain-specific evaluation  
zerorepo eval --benchmark ./ml_tasks --domain ml

# Quick evaluation
zerorepo eval --benchmark ./quick_tests --iterations 5
```

### Programmatic
```python
from zerorepo.eval.harness import EvaluationHarness

harness = EvaluationHarness(config)
results = await harness.run_benchmark(benchmark_path)
```

## 📋 Quality Monitoring

### Health Signals
- **Feature Generation Trends** - Linear growth with iterations
- **LOC Growth** - Consistent code production
- **Test Pass Rates** - Quality maintenance over time
- **Error Patterns** - Common failure modes

### Alerts
- **Generation Failures** - Systematic generation issues
- **Quality Degradation** - Declining test pass rates
- **Performance Issues** - Unusual generation times

---

*Comprehensive evaluation system for repository generation quality*