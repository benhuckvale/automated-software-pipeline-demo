# Components

Detailed documentation of each system component.

## Foundation Components

### WorkflowDefinition

Parsed from YAML workflow files:

```python
workflow = WorkflowDefinition(
    name="solve-simple",
    description="3-step TDD workflow",
    steps=[
        StepDefinition(
            id="clarify",
            model=ModelName.HAIKU,
            wrapper="claude_code",
            prompt_strategy="prompts/clarify_problem.md",
            outputs=["context/clarified_problem.md"],
            depends_on=[],
            timeout=180,
            max_turns=10
        ),
        # ... more steps
    ]
)
```

### WorkspaceInfo

Metadata about an execution workspace:

```python
workspace = create_workspace()
# workspace.workspace_id = "00001"
# workspace.project_dir = Path("workspaces/00001/project")
# workspace.context_dir = Path("workspaces/00001/context")
# etc.
```

### WorkflowState

Runtime state persisted after each step:

```python
state = WorkflowState(
    workflow_id="00001",
    workflow_name="solve-simple",
    started_at=datetime.now(),
    steps={
        "clarify": StepResult(
            step_id="clarify",
            status=StepStatus.COMPLETED,
            tokens_used=250,
            outputs={"context/clarified_problem.md": "abc123"}
        )
    },
    total_tokens=250
)
```

## Agent Components

### AgentExecutor (Base)

Abstract interface all agents implement:

```python
class AgentExecutor(ABC):
    @abstractmethod
    def execute_step(
        self,
        step: StepDefinition,
        workspace: WorkspaceInfo,
        context: dict[str, str] | None = None,
    ) -> StepResult:
        pass
```

### MockAgentExecutor

Testing executor that doesn't call APIs:

```python
executor = MockAgentExecutor()
result = executor.execute_step(step, workspace, context)
# Generates mock output files immediately
```

**Features**:
- Fast (< 1 second per step)
- Free (no API costs)
- Deterministic output
- Supports test directives in prompts

### ClaudeCodeExecutor

Production executor using Claude Code CLI:

```python
executor = ClaudeCodeExecutor()
result = executor.execute_step(step, workspace, context)
# Calls: claude -p "prompt" --model sonnet ...
```

**Features**:
- Real AI inference
- Configurable models (haiku/sonnet/opus)
- Timeout handling
- Tool auto-approval
- Subprocess isolation

## Orchestration Components

### WorkflowExecutor

Main orchestration engine:

```python
executor = WorkflowExecutor()

# Run new workflow
state = executor.run(workflow, workspace, problem_file, context)

# Resume interrupted workflow
state = executor.resume(workflow, workspace, context)
```

**Key Methods**:

- `run()`: Execute workflow from start
- `resume()`: Continue from saved state
- `_check_dependencies()`: Verify prerequisites
- `_execute_step()`: Run single step

**Execution Order**:
1. Resolve execution order (topological sort)
2. Initialize state (all steps PENDING)
3. For each step in order:
   - Check dependencies satisfied
   - Execute step
   - Save state
   - Stop on failure
4. Mark workflow complete

## CLI Components

### Commands

**run**: Start new workflow
```bash
pipeline run --workflow YAML --problem TXT
```

**resume**: Continue workflow
```bash
pipeline resume --workspace ID
```

**status**: Show state
```bash
pipeline status --workspace ID
```

**list**: List workspaces
```bash
pipeline list
```

### Output Format

Consistent formatting across all commands:

```
============================================================
✓ Workflow completed successfully

Workspace: 00001
Steps completed: 3/3
Total tokens: 750
Duration: 108.8s

Step Status:
  ✓ clarify: completed
  ✓ write_tests: completed
  ✓ build_solution: completed
============================================================
```

## Next Steps

- [Workflows](workflows.md) - How to define and customize workflows
- [Testing](../development/testing.md) - Testing strategies
