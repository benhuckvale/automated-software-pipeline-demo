# Contributing

Guidelines for contributing to the Automated Software Pipeline.

## Getting Started

1. **Fork and clone**:
   ```bash
   git clone https://github.com/yourusername/automated-software-pipeline-demo.git
   cd automated-software-pipeline-demo
   ```

2. **Install dev dependencies**:
   ```bash
   pdm install -G dev
   ```

3. **Run tests**:
   ```bash
   pdm run pytest tests/ -v
   ```

## Development Workflow

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**:
   - Write code
   - Add tests
   - Update docs

3. **Run tests**:
   ```bash
   pdm run pytest tests/ -v
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Add feature: description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**:
   - Go to GitHub
   - Create PR from your branch to main
   - Wait for CI checks
   - Address review feedback

## Code Standards

### Python Style

- **PEP 8** compliant
- **Type hints** on all functions
- **Docstrings** on public functions
- **Line length**: 100 characters

Example:

```python
def execute_step(
    self,
    step: StepDefinition,
    workspace: WorkspaceInfo,
    context: dict[str, str] | None = None,
) -> StepResult:
    """Execute a workflow step.

    Args:
        step: Step definition from workflow
        workspace: Workspace for execution
        context: Optional context variables

    Returns:
        StepResult with execution outcome
    """
    pass
```

### Testing

- **Write tests** for new features
- **Maintain coverage**: Aim for >80%
- **Test naming**: `test_<function>_<scenario>`
- **Use fixtures** for common setup

Example:

```python
def test_execute_step_success(self, workspace, mock_prompt):
    """Test successful step execution."""
    executor = MockAgentExecutor()
    result = executor.execute_step(step, workspace)
    assert result.status == StepStatus.COMPLETED
```

### Documentation

- **Update docs** for new features
- **Add examples** where helpful
- **Keep README** up to date

## Project Structure

```
src/pipeline/          # Core implementation
  __init__.py         # Package init, logging
  models.py           # Data models
  workspace.py        # Workspace management
  state.py            # State persistence
  parser.py           # YAML parsing
  executor.py         # Orchestration
  cli.py              # CLI interface
  agents/             # Agent implementations
    base.py           # Abstract interface
    mock.py           # Mock executor
    claude_code.py    # Claude Code executor

tests/                # Unit tests
  test_agents.py      # Agent tests
  test_executor.py    # Orchestration tests
  test_state.py       # State tests
  test_workspace.py   # Workspace tests

workflows/            # Workflow definitions
  test-mock.yaml      # Mock workflow
  solve-simple.yaml   # Production workflow

prompts/              # Prompt templates
  clarify_problem.md
  write_tests.md
  build_tdd.md

examples/             # Sample problems
  reverse_string/
  two_sum/

docs/                 # Documentation (MkDocs)
```

## Adding New Features

### New Agent Executor

1. Create class in `src/pipeline/agents/`:
   ```python
   from .base import AgentExecutor

   class MyAgentExecutor(AgentExecutor):
       def execute_step(self, step, workspace, context):
           # Implementation
           pass
   ```

2. Register in `executor.py`:
   ```python
   self._agents["my_agent"] = MyAgentExecutor()
   ```

3. Add tests in `tests/test_agents.py`

### New CLI Command

1. Add function in `cli.py`:
   ```python
   def cmd_my_command(args):
       # Implementation
       pass
   ```

2. Register in `main()`:
   ```python
   parser = subparsers.add_parser("mycommand", help="...")
   commands["mycommand"] = cmd_my_command
   ```

3. Update docs

### New Workflow

1. Create YAML in `workflows/`:
   ```yaml
   workflow:
     name: my-workflow
     steps: [...]
   ```

2. Create prompts in `prompts/`

3. Test with mock executor first

4. Document in `docs/architecture/workflows.md`

## Testing Guidelines

### Unit Tests

Test individual components in isolation:

```python
def test_create_workspace():
    """Test workspace creation."""
    ws = create_workspace(base_dir=tmp_path)
    assert ws.workspace_path.exists()
    assert ws.project_dir.exists()
```

### Integration Tests

Test components working together:

```python
def test_workflow_execution():
    """Test full workflow execution."""
    executor = WorkflowExecutor()
    state = executor.run(workflow, workspace)
    assert state.is_complete
```

### End-to-End Tests

Test complete user workflows:

```bash
# Run in CI
pdm run pipeline run --workflow workflows/test-mock.yaml --problem examples/reverse_string/problem.txt
```

## Pull Request Process

1. **Ensure tests pass**:
   ```bash
   pdm run pytest tests/ -v
   ```

2. **Update documentation**

3. **Write clear commit messages**:
   ```
   Add feature: brief description

   - Detailed change 1
   - Detailed change 2

   Closes #123
   ```

4. **Submit PR** with:
   - Clear description
   - Link to related issues
   - Screenshots if UI changes

5. **Address feedback**

## Getting Help

- **Issues**: Open GitHub issue
- **Discussions**: Use GitHub Discussions
- **Questions**: Tag with `question` label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
