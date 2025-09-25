#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  BUILD PROJECT: ZeroRepo — Graph-Driven Repository Generation
  
  Objective: Build an agentic system that (1) plans a software repository as a Repository Planning Graph (RPG), 
  (2) refines it into file/data-flow/function designs, then (3) generates code topologically with test-driven 
  validation and graph-guided localization & editing.
  
  The system should have three main stages:
  - Stage A: Proposal-Level Construction (Capabilities graph with explore/exploit/missing features)
  - Stage B: Implementation-Level Construction (File structure + data-flow & interface encoding) 
  - Stage C: Graph-Guided Code Generation (Topological traversal with TDD)
  
  Key components: RPG data models, prompt templates, orchestration logic, tools & utilities, 
  evaluation harness, and CLI interface.

backend:
  - task: "ZeroRepo Core Data Models (RPG nodes/edges, interfaces)"
    implemented: true
    working: true
    file: "zerorepo/core/models.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Complete RPG data models with pydantic validation implemented"

  - task: "Graph Operations and DAG Validation"
    implemented: true
    working: true
    file: "zerorepo/rpg/graph_ops.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "NetworkX-based graph operations with topological sorting implemented"

  - task: "Proposal Controller (Stage A - Explore/Exploit/Missing)"
    implemented: true
    working: true
    file: "zerorepo/plan/proposal.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Complete proposal stage with feature selection strategies implemented"

  - task: "Implementation Controller (Stage B - File Structure & Interfaces)"
    implemented: true
    working: true
    file: "zerorepo/plan/implementation.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Implementation stage with file mapping and interface generation implemented"

  - task: "Code Generator (Stage C - Topological TDD)"
    implemented: true
    working: true
    file: "zerorepo/codegen/generator.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Graph-guided code generation with test-driven development implemented"

  - task: "LLM Client (Emergent Integration)"
    implemented: true
    working: true
    file: "zerorepo/tools/llm_client.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Unified LLM client with Emergent key integration implemented"

  - task: "Vector Store (FAISS-based Feature Search)"
    implemented: true
    working: true
    file: "zerorepo/tools/vector_store.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "FAISS vector store with semantic feature search and ontology loading implemented"

  - task: "Docker Test Runner"
    implemented: true
    working: true
    file: "zerorepo/tools/docker_runtime.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Docker-based test execution with subprocess fallback implemented"

  - task: "Main Orchestrator"
    implemented: true
    working: true
    file: "zerorepo/orchestrator.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Complete three-stage pipeline orchestration implemented"

  - task: "CLI Interface"
    implemented: true
    working: true
    file: "zerorepo/cli/main.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Typer-based CLI with plan/build/generate commands implemented"

  - task: "FastAPI Integration"
    implemented: true
    working: true
    file: "server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Complete REST API with ZeroRepo endpoints and background job processing"

  - task: "Prompt Templates"
    implemented: true
    working: true
    file: "zerorepo/prompts/templates.yaml"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "YAML-based prompt templates from paper specifications implemented"

frontend:
  - task: "ZeroRepo Web Interface"
    implemented: true
    working: true
    file: "App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Complete React interface with demo functionality, planning, and generation features"

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "ZeroRepo system full implementation completed"
    - "Quick demo functionality verified"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "COMPLETE: Implemented comprehensive ZeroRepo system with all three stages (Proposal → Implementation → Code Generation). Includes FastAPI backend, React frontend, CLI interface, and working demo. System successfully generates repository planning graphs using explore/exploit/missing feature strategies."