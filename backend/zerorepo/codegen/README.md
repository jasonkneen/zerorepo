# Code Generation

Topological code generation with test-driven development for ZeroRepo.

## 🏗️ Generation Process

### Stage C: Code Generation
1. **Topological Traversal** - Dependency-ordered processing
2. **Test Generation** - Comprehensive test creation from specifications
3. **Implementation Generation** - AI-powered code creation
4. **Iterative Improvement** - Test-driven refinement (up to 8 attempts)
5. **Graph-Guided Debugging** - Context-aware error resolution

## 🧪 Test-Driven Development

### TDD Cycle
```python
from zerorepo.codegen.generator import CodeGenerator

generator = CodeGenerator(config, llm_client, docker_runner)

# Generate repository with TDD
result = await generator.generate_repository(rpg, interfaces, output_dir)
```

### Process Flow
1. **Interface Analysis** - Parse function/class specifications
2. **Test Generation** - Create pytest test from docstring and signature
3. **Initial Implementation** - Generate code stub with AI
4. **Test Execution** - Run tests in isolated Docker environment
5. **Debug and Fix** - Use graph context to improve failing implementations
6. **Validation** - Repeat until tests pass or max retries reached

## 🐳 Test Execution

### Docker Runtime
- **Isolated Environment** - Sandboxed test execution
- **Resource Limits** - Memory and CPU constraints
- **Network Isolation** - No external access during testing
- **Subprocess Fallback** - Works without Docker if needed

### Test Analysis
- **Pass Rate Tracking** - Monitor generation success
- **Error Classification** - Distinguish implementation vs environment issues
- **Performance Metrics** - Execution time and resource usage

## 🔧 Debugging Features

### Graph-Guided Localization
- **Functionality Search** - Find relevant components by capability
- **Dependency Exploration** - Trace relationships and data flows
- **Neighborhood Analysis** - Context-aware debugging suggestions

### Fix Generation
- **Minimal Patches** - Targeted improvements
- **Context Preservation** - Maintain original interface contracts
- **Iterative Refinement** - Progressive improvement with AI feedback

## 📈 Metrics and Monitoring

### Generation Metrics
- Files generated vs attempted
- Test pass rates
- Lines of code produced
- Generation time per component

### Quality Metrics
- Interface compliance
- Test coverage
- Documentation completeness
- Code style consistency

---

*Implements topological code generation with test-driven development*