# Automated Software Pipeline Demo - Implementation Plan

## Project Overview

**Goal**: Build an automated software delivery pipeline that solves coding problems (leetcode-style) through multiple AI-driven workflow steps.

**Scope**: Small, focused on leetcode-style problems. Solutions are simple, single-file Python scripts that can be created and reviewed quickly with minimal code.

**Key Features**:
- Multi-step workflow execution (clarification → planning → building → review → documentation)
- Test-driven development with iterative refinement
- Configurable worker pool with model selection per step
- Generic workflow definition supporting DAG-based execution
- Resumable workflows with file-based state persistence
- Initial focus: local execution with Claude Code
- Future: GitHub Actions / GitLab CI integration

## Two Layers of Code

### 1. The Pipeline System (what we're building)
- **Language**: Python with pyproject.toml and pdm
- **Purpose**: Orchestrates workflows, manages state, executes AI agents
- **Dependencies**: pydantic, structlog, subprocess
- **Interface**: CLI tool using argparse

### 2. The Solutions (what the pipeline produces)
- **Format**: Single `.py` files (self-contained, no external dependencies)
- **Structure**:
  - Solution function(s) following naming convention: `solve_<problem>_with_<approach>`
  - Embedded unittest test cases
  - `if __name__ == "__main__"` block supporting:
    - `--test` flag to run tests
    - Problem-specific args or input file for running the solution
- **Examples**:
  - `solve_two_sum_with_hashmap(nums, target)`
  - `find_longest_substring_with_sliding_window(s)`
  - `reverse_linked_list_with_iteration(head)`

## Architecture

### Core Components

1. **Workflow Definition System**
   - Format: YAML-based workflow definitions
   - Defines: steps, dependencies, model selection, input/output artifacts
   - Supports: DAG-based execution (steps run when dependencies are met)

2. **Workflow Engine/Orchestrator**
   - Parses and validates workflow definitions using Pydantic models
   - Manages step execution order based on dependency graph
   - Handles worker pool coordination
   - State persistence: file-based JSON in workspace directory
   - Supports resuming interrupted workflows

3. **Worker Pool Manager**
   - Configurable pool size (MVP: start with N=1)
   - Assigns tasks to available workers when dependencies are satisfied
   - Workers created on-demand (no pre-spawning in MVP)
   - Priority: Execute available tasks in dependency order; ties broken arbitrarily

4. **Agent Executor Abstraction**
   - Interface for invoking different LLM wrappers (MVP: Claude Code via subprocess)
   - Handles model selection per step (haiku/sonnet/opus)
   - Manages sandboxed execution (folder-based restriction, no Docker in MVP)
   - Tracks token usage per step

5. **Artifact Management**
   - Workspace structure: `workspaces/<build-number>/`
     - `project/`: The solution code being built
     - `context/`: Artifacts passed between steps
     - `state/`: Workflow state and metadata
   - Completed steps save outputs to context directory
   - Failed attempts preserved for future recovery

### Prompt Strategy Files

Prompt templates are separate markdown files with YAML frontmatter defining execution strategy.

**Structure**:
```markdown
---
strategy:
  type: loop | sequential | branch
  max_iterations: 5
  success_criteria:
    - command: "python {workspace}/project/solution.py --test"
    - check: "file_exists {workspace}/project/solution.py"
    - question: "Does the solution handle all edge cases?"
prompts:
  - id: initial
    next: check_tests
  - id: check_tests
    next: refine | done
  - id: refine
    next: check_tests
---

# Initial Prompt
Write a Python solution for {problem_name}...

---

# Check Tests Prompt
Review the test results. If all pass, respond "DONE". Otherwise, continue to refine.

---

# Refine Prompt
The tests failed with the following errors:
{test_output}

Fix the implementation...
```

**Success Criteria Types**:
- `command`: Shell command to execute (exit code 0 = success)
- `check`: Logical check implemented by the system (e.g., `file_exists`, `tests_pass`)
- `question`: Natural language question for agent to evaluate

### Workflow Definition Format

```yaml
workflow:
  name: "solve-two-sum"

  steps:
    - id: clarify
      type: agent_task
      model: haiku
      wrapper: claude_code
      prompt_strategy: "prompts/clarify_problem.md"
      inputs:
        - problem_statement.txt
      outputs:
        - clarified_problem.md

    - id: write_tests
      type: agent_task
      model: sonnet
      wrapper: claude_code
      depends_on: [clarify]
      prompt_strategy: "prompts/write_tests.md"
      inputs:
        - context/clarified_problem.md
      outputs:
        - project/solution.py  # with tests, no implementation yet

    - id: build_solution
      type: agent_task
      model: sonnet
      wrapper: claude_code
      depends_on: [write_tests]
      prompt_strategy: "prompts/build_tdd.md"
      inputs:
        - project/solution.py
      outputs:
        - project/solution.py  # now with passing implementation

    - id: review
      type: agent_task
      model: sonnet
      wrapper: claude_code
      depends_on: [build_solution]
      prompt_strategy: "prompts/review_code.md"
      inputs:
        - project/solution.py
      outputs:
        - review_notes.md

    - id: refine
      type: agent_task
      model: sonnet
      wrapper: claude_code
      depends_on: [review]
      prompt_strategy: "prompts/refine_solution.md"
      inputs:
        - project/solution.py
        - context/review_notes.md
      outputs:
        - project/solution.py  # refined version
```

## Implementation Phases

### Phase 1: Local Runner MVP ⭐ **START HERE**

**Goal**: Run a 3-step workflow locally using Claude Code (clarify → write tests → build solution)

**Workflow Steps**:
1. **Problem Clarification**: Analyze problem statement, identify edge cases, clarify requirements
2. **Test Design**: Write comprehensive test cases in solution.py (no implementation yet)
3. **Building (TDD Loop)**: Implement solution, run tests, fix failures iteratively until passing

**Components to Build**:
1. Project scaffolding (pyproject.toml, pdm setup, CLI entry point)
2. Pydantic models for workflow definition and state
3. YAML workflow parser with validation
4. Sequential executor (no parallelism yet; execute steps in dependency order)
5. Claude Code subprocess wrapper with model selection
6. File-based artifact management and state persistence
7. Structured logging with structlog (logs saved to workspace)

**Technology Stack**:
- Python 3.11+
- pdm for dependency management
- pydantic for config/state validation
- structlog for structured logging
- argparse for CLI
- subprocess for agent execution
- PyYAML for workflow parsing

**Test Problems** (start simple):
- Reverse a string
- Two sum with hashmap
- Binary search

**Success Criteria**:
- Can run `pipeline run --workflow workflows/solve-problem.yaml --problem examples/reverse_string/problem.txt`
- Pipeline creates workspace, executes 3 steps sequentially
- Outputs working solution.py with tests and implementation
- Can resume interrupted workflow with `pipeline resume --workspace workspaces/00001`
- Logs show clear progress through each step
- Total runtime < 5 minutes for simple problems

### Phase 2: Code Review & Refinement

**Goal**: Add review step to catch code quality issues and refine solutions

**New Workflow Steps**:
4. **Code Review**: Quality check, identify improvements, suggest optimizations
5. **Refine**: Apply review feedback, improve code quality

**Test Problems** (slightly more complex):
- Problems that can have "ugly" initial solutions (nested loops, poor variable names)
- Problems where optimization is possible (O(n²) → O(n))

**Success Criteria**:
- Pipeline can identify quality issues in initial solutions
- Refinement step produces cleaner, more readable code
- Review notes are preserved in context for reference

### Phase 3: Performance Analysis & Benchmarking

**Goal**: Add performance comparison for multiple algorithmic approaches

**New Workflow Steps**:
6. **Performance Analysis**: Analyze time/space complexity, identify bottlenecks
7. **Benchmarking**: Run solutions with various input sizes, measure actual performance
8. **Comparison**: Compare multiple approaches, recommend optimal solution

**Test Problems** (harder with multiple approaches):
- Problems solvable with different complexity classes (e.g., O(n log n) vs O(n²))
- Problems where approach choice matters (dynamic programming vs recursion)

**Success Criteria**:
- Pipeline can implement same problem with multiple approaches
- Benchmarking runs fairly (same machine state, comparable conditions)
- Clear performance comparison with complexity analysis
- Recommendation based on actual measurements

### Phase 4: Documentation & Polish

**Goal**: Generate comprehensive documentation for solutions

**New Workflow Steps**:
9. **Documentation**: Generate solution explanation, approach description, complexity analysis

**Success Criteria**:
- Solutions include clear docstrings and comments
- Approach explanation documents algorithm choice
- Complexity analysis is accurate and thorough

### Future: Worker Pool & Parallelism

**Goal**: Support concurrent step execution where dependencies allow

**Features**:
- Execute independent steps in parallel (e.g., if two steps both depend on step 1, run them concurrently)
- Worker pool with configurable size (control parallelism)
- Fair scheduling when multiple steps are ready

**Implementation**:
- Use threading or asyncio for concurrent execution
- Maintain dependency graph to identify ready tasks
- Worker pool manager assigns tasks to available workers

### Future: CI/CD Integration

**Goal**: Generate GitHub Actions workflows from pipeline definitions (proof of abstraction)

**Features**:
- Translate workflow YAML to GitHub Actions YAML
- Use Anthropic API instead of local Claude Code
- Secret management for API keys
- Artifact upload/download between jobs

**Note**: Focus on local execution for now; CI/CD is future work

## Project Structure

```
automated-software-pipeline-demo/
├── pyproject.toml           # Project dependencies and metadata
├── README.md                # Project documentation
├── plan.md                  # This file
│
├── src/
│   └── pipeline/
│       ├── __init__.py
│       ├── cli.py           # CLI entry point (argparse)
│       ├── models.py        # Pydantic models for workflow/state
│       ├── parser.py        # YAML workflow parser
│       ├── executor.py      # Orchestration engine
│       ├── state.py         # State management (save/load/resume)
│       ├── workspace.py     # Workspace management
│       └── agents/
│           ├── __init__.py
│           ├── base.py      # Abstract agent interface
│           └── claude_code.py  # Claude Code subprocess wrapper
│
├── workflows/               # Workflow definitions
│   ├── solve-simple.yaml    # MVP 3-step workflow
│   ├── solve-with-review.yaml  # Phase 2: with review
│   └── solve-with-perf.yaml    # Phase 3: with performance
│
├── prompts/                 # Prompt strategy files
│   ├── clarify_problem.md
│   ├── write_tests.md
│   ├── build_tdd.md
│   ├── review_code.md
│   ├── refine_solution.md
│   ├── analyze_performance.md
│   └── benchmark.md
│
├── examples/                # Example problems
│   ├── reverse_string/
│   │   └── problem.txt
│   ├── two_sum/
│   │   └── problem.txt
│   └── binary_search/
│       └── problem.txt
│
├── workspaces/              # Execution workspaces (gitignored)
│   └── 00001/
│       ├── project/
│       │   └── solution.py
│       ├── context/
│       │   ├── clarified_problem.md
│       │   └── review_notes.md
│       ├── state/
│       │   └── workflow_state.json
│       └── logs/
│           └── pipeline.log
│
└── tests/                   # Tests for the pipeline itself
    ├── test_parser.py
    ├── test_executor.py
    └── test_state.py
```

## Workflow State Schema

State is persisted as JSON in `workspaces/<id>/state/workflow_state.json`:

```json
{
  "workflow_id": "00001",
  "workflow_name": "solve-two-sum",
  "status": "in_progress",
  "created_at": "2026-02-16T10:30:00Z",
  "updated_at": "2026-02-16T10:32:15Z",

  "completed_steps": [
    {
      "step_id": "clarify",
      "status": "success",
      "started_at": "2026-02-16T10:30:00Z",
      "completed_at": "2026-02-16T10:30:45Z",
      "model": "haiku",
      "attempts": 1,
      "outputs": ["context/clarified_problem.md"],
      "tokens_used": 1247
    },
    {
      "step_id": "write_tests",
      "status": "success",
      "started_at": "2026-02-16T10:30:45Z",
      "completed_at": "2026-02-16T10:31:30Z",
      "model": "sonnet",
      "attempts": 2,
      "outputs": ["project/solution.py"],
      "tokens_used": 3451,
      "failed_attempts": [
        {
          "attempt": 1,
          "error": "Tests incomplete, missing edge case coverage",
          "timestamp": "2026-02-16T10:31:15Z"
        }
      ]
    }
  ],

  "current_step": "build_solution",
  "pending_steps": ["review", "refine"],

  "total_tokens_used": 4698
}
```

**Resumability**: When resuming, the executor:
1. Loads state from workspace
2. Identifies completed steps (can skip)
3. Identifies current step (may need recovery prompt if previous attempt failed)
4. Continues execution from current step

## Error Handling & Recovery

**Strategy**: Support resumable workflows with optional recovery prompts

**Failure Handling**:
1. **Immediate failure**: Step fails quickly (e.g., file not found, invalid syntax)
   - Save failure to state with error details
   - Allow manual inspection and fix before resume

2. **Iteration exhaustion**: Step hits max_iterations without success
   - Save all attempts to state
   - Option: Run recovery prompt to get back on track
   - Option: Fail fast and require manual intervention

3. **Partial success**: Some success criteria met but not all
   - Save progress
   - Allow resume with context from previous attempts

**Recovery Prompts**: Optional "meta-prompts" that analyze failures and adjust approach before retrying original prompt strategy.

## Logging & Observability

**Logging**: Structured logs using structlog
- **Format**: JSON lines for easy parsing
- **Location**: `workspaces/<id>/logs/pipeline.log`
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Context**: Each log entry includes workflow_id, step_id, timestamp

**Metrics Tracked**:
- Total workflow runtime
- Per-step execution time
- Token usage per step and total
- Success/failure rates
- Retry counts

**Future Dashboard** (separate process):
- Monitors `workspaces/` directory
- Shows live progress of running workflows
- Displays logs and state in real-time
- Not needed for MVP

## Success Criteria

### MVP (Phase 1) Success
- ✅ Can solve a simple coding problem end-to-end without manual intervention
- ✅ Input: problem statement text file
- ✅ Output: working solution.py with tests and passing implementation
- ✅ Uses 3 workflow steps (clarify → write tests → build)
- ✅ State persisted to files, workflow is resumable
- ✅ Structured logs show clear progress
- ✅ Total runtime < 5 minutes for simple problems
- ✅ At least 2 different example problems solved successfully

### Phase 2 Success
- ✅ Code review step identifies quality issues
- ✅ Refinement step produces cleaner code
- ✅ Tested on problems that produce "ugly" initial solutions

### Phase 3 Success
- ✅ Multiple algorithmic approaches implemented for same problem
- ✅ Fair performance benchmarking
- ✅ Clear comparison with complexity analysis and recommendations

### Phase 4 Success
- ✅ Solutions include comprehensive documentation
- ✅ Approach rationale clearly explained
- ✅ Complexity analysis accurate and thorough

## Next Steps

1. **Set up project structure** (pyproject.toml, pdm init, directory layout)
2. **Define Pydantic models** (WorkflowDefinition, StepDefinition, WorkflowState)
3. **Build workflow parser** (parse YAML, validate against models)
4. **Implement workspace management** (create directories, manage artifacts)
5. **Build Claude Code executor** (subprocess invocation with model selection)
6. **Implement state persistence** (save/load workflow state)
7. **Build sequential executor** (run steps in dependency order)
8. **Create MVP workflow** (`workflows/solve-simple.yaml` with 3 steps)
9. **Write prompt strategy files** (clarify, write_tests, build_tdd)
10. **Add example problems** (reverse_string, two_sum)
11. **Implement CLI** (run, resume commands)
12. **Test end-to-end** with simplest problem
13. **Add structured logging**
14. **Iterate and refine** based on learnings

---

## Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Programming Language | Python | Wide ecosystem, good for AI integration, fast iteration |
| Dependency Manager | pdm | Modern, fast, good pyproject.toml support |
| Config Format | YAML + Pydantic | Human-readable, validated structure |
| State Persistence | JSON files | Simple, inspectable, supports resumability |
| Agent Interface | Subprocess | Clean isolation, easy to swap implementations |
| Sandbox | Folder restriction | Sufficient for simple problems, no Docker overhead |
| Logging | structlog | Structured, easy to parse, flexible |
| Prompt Strategy | Markdown with YAML frontmatter | Clear documentation, flexible execution logic |
| Context Passing | Files in workspace | Simple, inspectable, supports any data type |
| Execution Model | Sequential → DAG → Parallel | Progressive enhancement, start simple |
| Function Naming | `solve_<problem>_with_<approach>` | Descriptive, verb-based, clear intent |
| Solution Format | Single .py with tests | Self-contained, easy to review and run |

---

**Inspiration**: ~/dev/codility project (preview planning, multiple algorithms, complexity analysis)

**Focus**: Generic solution, not tied to specific platforms; prove local execution model before CI/CD integration
