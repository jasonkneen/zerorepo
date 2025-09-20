# ZeroRepo Prompt Templates

LLM prompt templates for the ZeroRepo system, based on research paper specifications.

## 📝 Template Categories

### Proposal Stage (Stage A)
- **`proposal_exploit_select`** - High-relevance feature selection
- **`proposal_explore_select`** - Diversity injection and breadth
- **`proposal_missing_features`** - Gap identification and synthesis

### Implementation Stage (Stage B)
- **`impl_folder_layout`** - File system structure mapping
- **`impl_file_assignment`** - Feature to file assignment
- **`impl_base_classes`** - Shared abstraction identification
- **`impl_interfaces`** - Interface specification generation

### Code Generation Stage (Stage C)
- **`codegen_unit_tests`** - Test generation from specifications
- **`debug_localize_and_fix`** - Graph-guided debugging

## 🎯 Template Format

### YAML Structure
```yaml
template_name:
  name: "template_name"
  description: "Brief description"
  instructions: |
    Detailed instructions for the LLM
    with specific requirements and constraints
  sources:
    - "Paper reference or section"
```

### System Prompts
- **`system_json_mode`** - JSON response formatting
- **`system_code_generation`** - Code quality standards
- **`system_graph_analysis`** - Graph-guided analysis

## 🔬 Research Foundation

Templates are derived from ["Repository Planning Graphs for Agentic Software Development"](https://arxiv.org/abs/2509.16198):

- **Appendix A.3** - Proposal stage templates
- **Appendix B.1** - Implementation stage templates  
- **Section 4** - Code generation and validation
- **Appendix C** - Debugging and localization

## 🛠️ Usage

### Loading Templates
```python
from zerorepo.prompts.loader import PromptLoader

loader = PromptLoader("templates.yaml")
template = loader.get_template("proposal_exploit_select")
```

### Template Variables
- **`{project_goal}`** - User-provided objective
- **`{domain}`** - Problem domain (ml, web, data, general)
- **`{current_features}`** - Existing feature context
- **`{similar_features}`** - Retrieved similar features

## 📊 Quality Control

### Template Standards
- **Deterministic** - Consistent outputs for same inputs
- **Specific** - Clear requirements and constraints
- **Structured** - Well-defined output formats
- **Contextual** - Domain-aware instructions

### Validation
- JSON schema compliance
- Output format consistency
- Response quality assessment
- Error handling instructions

---

*LLM prompt templates for consistent, high-quality AI interactions*