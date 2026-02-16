# Architecture Overview

The pipeline follows a layered architecture with clear separation of concerns.

## System Layers

```
┌─────────────────────────────────────┐
│          CLI Layer                  │  User interaction
│        (src/pipeline/cli.py)        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Orchestration Layer            │  Workflow execution
│     (src/pipeline/executor.py)      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Agent Execution Layer          │  Step execution
│    (src/pipeline/agents/*.py)       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Foundation Layer               │  Core services
│  (models, workspace, state, parser) │
└─────────────────────────────────────┘
```

## Core Components

### 1. Foundation Layer

**Purpose**: Core data structures and services

- **models.py**: Pydantic models for type-safe data
  - `WorkflowDefinition`, `StepDefinition`
  - `WorkflowState`, `StepResult`
  - `WorkspaceInfo`

- **workspace.py**: Workspace lifecycle management
  - Auto-incrementing build numbers
  - Directory structure creation
  - File management

- **state.py**: Persistent state management
  - Atomic writes with temp files
  - JSON serialization via Pydantic
  - Resume capability detection

- **parser.py**: YAML workflow parsing
  - Validation with Pydantic
  - Circular dependency detection
  - Topological sort for execution order

### 2. Agent Execution Layer

**Purpose**: Execute workflow steps using different backends

- **base.py**: Abstract `AgentExecutor` interface
  - Prompt template loading
  - Variable substitution
  - Output validation

- **mock.py**: `MockAgentExecutor` for testing
  - No API calls - generates predetermined outputs
  - Supports directives: `MOCK_FAIL`, `MOCK_SLOW`
  - Fast, free testing

- **claude_code.py**: `ClaudeCodeExecutor` for production
  - Subprocess invocation of Claude CLI
  - Timeout handling, output parsing
  - Tool auto-approval

### 3. Orchestration Layer

**Purpose**: Coordinate multi-step workflow execution

- **executor.py**: `WorkflowExecutor`
  - Topological sort for dependency resolution
  - Sequential step execution
  - State persistence after each step
  - Fail-fast error handling
  - Resume from saved state

### 4. CLI Layer

**Purpose**: User interaction

- **cli.py**: Command-line interface
  - `run`: Start new workflow
  - `resume`: Continue interrupted workflow
  - `status`: Show execution state
  - `list`: List all workspaces

## Data Flow

1. **User** invokes CLI command
2. **CLI** parses arguments, loads workflow YAML
3. **Parser** validates workflow, resolves dependencies
4. **Executor** creates workspace, orchestrates steps
5. **Agent** executes each step (mock or Claude Code)
6. **State** persists after each step
7. **CLI** displays results

## Workspace Structure

Each execution gets an isolated workspace:

```
workspaces/
  00001/
    project/        # Code outputs
      solution.py
    context/        # Problem files, clarifications
      problem.txt
      clarified_problem.md
    state/          # Workflow state
      workflow_state.json
    logs/           # Execution logs
      pipeline.log
```

## Key Design Patterns

### 1. Test Mixin Pattern

Tests are reusable across multiple implementations:

```python
class TestMixinReverse_string:
    reverse_string = None  # Set by concrete classes

    def test_basic(self):
        assert self.reverse_string("hello") == "olleh"

class TestReverseStringUsingSlicing(TestMixinReverse_string, unittest.TestCase):
    reverse_string = staticmethod(reverse_string_using_slicing)
```

### 2. Dependency Injection

Agent executors are registered and selected at runtime:

```python
executor = WorkflowExecutor()
executor.register_agent("custom", CustomAgentExecutor())
```

### 3. State Machine

Workflow progresses through clear states:

```
PENDING → IN_PROGRESS → COMPLETED
                ↓
              FAILED
```

## Next Steps

- [Components](components.md) - Detailed component documentation
- [Workflows](workflows.md) - How workflows are defined and executed
