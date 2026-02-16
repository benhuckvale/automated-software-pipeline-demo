# Testing

Comprehensive guide to testing the pipeline.

## Test Suite Overview

The project has 33 unit tests covering all components:

```bash
pdm run pytest tests/ -v
```

**Test breakdown:**
- `test_agents.py`: 5 tests (agent executors)
- `test_executor.py`: 10 tests (orchestration)
- `test_state.py`: 6 tests (state management)
- `test_workspace.py`: 12 tests (workspace operations)

## Running Tests

### All Tests

```bash
pdm run pytest tests/ -v
```

### Specific Test File

```bash
pdm run pytest tests/test_agents.py -v
```

### Specific Test

```bash
pdm run pytest tests/test_agents.py::TestMockAgentExecutor::test_mock_executor_success -v
```

### With Coverage

```bash
pdm run pytest tests/ --cov=src/pipeline --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

## Test Structure

### Using Pytest Fixtures

```python
@pytest.fixture
def workspace(self, tmp_path):
    """Create a temporary workspace for testing."""
    ws_path = tmp_path / "00001"
    ws_path.mkdir()
    (ws_path / "project").mkdir()
    (ws_path / "context").mkdir()
    (ws_path / "state").mkdir()
    (ws_path / "logs").mkdir()

    return WorkspaceInfo.from_path(ws_path)

def test_with_workspace(self, workspace):
    """Test using the workspace fixture."""
    assert workspace.workspace_path.exists()
```

### Test Classes

Group related tests:

```python
class TestMockAgentExecutor:
    """Tests for MockAgentExecutor."""

    def test_success(self):
        pass

    def test_failure(self):
        pass
```

## Mock Executor for Testing

The `MockAgentExecutor` enables fast, free testing:

```python
from pipeline.agents.mock import MockAgentExecutor

executor = MockAgentExecutor()
result = executor.execute_step(step, workspace, context)

# Fast execution (< 1s)
# No API costs
# Deterministic output
```

### Mock Directives

Control mock behavior via prompts:

```python
# Trigger failure
prompt = "MOCK_FAIL"

# Add delay
prompt = "MOCK_SLOW"

# Normal success
prompt = "Test prompt"
```

## Integration Testing

Test components working together:

```python
def test_full_workflow_execution(self, workspace, mock_prompt):
    """Test complete workflow with multiple steps."""
    workflow = WorkflowDefinition(
        name="test",
        steps=[step1, step2, step3]
    )

    executor = WorkflowExecutor()
    state = executor.run(workflow, workspace)

    assert state.is_complete
    assert not state.has_failures
    assert len(state.completed_steps) == 3
```

## End-to-End Testing

Test the entire pipeline:

```bash
# Run mock workflow
pdm run pipeline run \
  --workflow workflows/test-mock.yaml \
  --problem examples/reverse_string/problem.txt

# Check results
test -f workspaces/00001/project/solution.py
test -f workspaces/00001/context/clarified_problem.md
```

## Continuous Integration

GitHub Actions runs tests automatically:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: pdm run pytest tests/ -v --tb=short

- name: Test mock workflow
  run: |
    pdm run pipeline run \
      --workflow workflows/test-mock.yaml \
      --problem examples/reverse_string/problem.txt
```

## Writing New Tests

### 1. Identify What to Test

- New feature added
- Bug fixed
- Edge case discovered

### 2. Choose Test Level

- **Unit**: Test single function/class
- **Integration**: Test components together
- **E2E**: Test full user workflow

### 3. Write Test

```python
def test_new_feature(self):
    """Test description of what you're testing."""
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

### 4. Run Test

```bash
pdm run pytest tests/test_file.py::test_new_feature -v
```

### 5. Verify Coverage

```bash
pdm run pytest tests/ --cov=src/pipeline
```

## Test Best Practices

### ✅ Do

- **Test behavior, not implementation**
- **Use descriptive test names**
- **Keep tests independent**
- **Use fixtures for setup**
- **Test edge cases**

### ❌ Don't

- **Don't test private methods directly**
- **Don't rely on test execution order**
- **Don't use global state**
- **Don't write flaky tests**

## Debugging Tests

### Print Output

```python
def test_debug(self):
    result = function()
    print(f"Result: {result}")  # Shown with pytest -s
    assert result == expected
```

Run with:
```bash
pytest tests/test_file.py::test_debug -v -s
```

### Use Debugger

```python
def test_debug(self):
    import pdb; pdb.set_trace()
    result = function()
    assert result == expected
```

### Check Logs

```python
import structlog
logger = structlog.get_logger()

def test_with_logs(caplog):
    function_that_logs()
    assert "expected message" in caplog.text
```

## Performance Testing

### Benchmark Tests

```python
def test_performance(self):
    import time

    start = time.time()
    result = function()
    elapsed = time.time() - start

    assert elapsed < 1.0  # Should complete in < 1 second
```

### Profile Tests

```bash
pytest tests/ --profile
```

## Test Coverage Goals

- **Overall**: >80%
- **Critical paths**: >95%
- **New code**: 100%

Current coverage:
```bash
pdm run pytest tests/ --cov=src/pipeline --cov-report=term
```

## Next Steps

- [Contributing](contributing.md) - Contribution guidelines
- [Components](../architecture/components.md) - System architecture
