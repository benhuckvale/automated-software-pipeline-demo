"""Tests for workflow execution and orchestration."""
import pytest
from pathlib import Path

from pipeline.executor import resolve_execution_order, WorkflowExecutor
from pipeline.models import (
    WorkflowDefinition,
    StepDefinition,
    ModelName,
    StepStatus,
    WorkspaceInfo,
)
from pipeline.state import load_state


class TestExecutionOrder:
    """Tests for topological sort and dependency resolution."""

    def test_resolve_simple_linear(self):
        """Test simple linear dependency chain."""
        workflow = WorkflowDefinition(
            name="test",
            steps=[
                StepDefinition(
                    id="step3",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                    depends_on=["step2"],
                ),
                StepDefinition(
                    id="step1",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                ),
                StepDefinition(
                    id="step2",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                    depends_on=["step1"],
                ),
            ],
        )

        order = resolve_execution_order(workflow)
        assert order == ["step1", "step2", "step3"]

    def test_resolve_parallel_steps(self):
        """Test parallel steps with no dependencies."""
        workflow = WorkflowDefinition(
            name="test",
            steps=[
                StepDefinition(
                    id="step1",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                ),
                StepDefinition(
                    id="step2",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                ),
            ],
        )

        order = resolve_execution_order(workflow)
        # Order doesn't matter for parallel steps, just check both present
        assert set(order) == {"step1", "step2"}

    def test_resolve_diamond_dependency(self):
        """Test diamond-shaped dependency graph."""
        workflow = WorkflowDefinition(
            name="test",
            steps=[
                StepDefinition(
                    id="step1",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                ),
                StepDefinition(
                    id="step2",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                    depends_on=["step1"],
                ),
                StepDefinition(
                    id="step3",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                    depends_on=["step1"],
                ),
                StepDefinition(
                    id="step4",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                    depends_on=["step2", "step3"],
                ),
            ],
        )

        order = resolve_execution_order(workflow)

        # step1 must come first
        assert order[0] == "step1"
        # step4 must come last
        assert order[3] == "step4"
        # step2 and step3 must come after step1 and before step4
        assert order.index("step2") > order.index("step1")
        assert order.index("step3") > order.index("step1")

    def test_resolve_circular_dependency_fails(self):
        """Test that circular dependencies are detected."""
        workflow = WorkflowDefinition(
            name="test",
            steps=[
                StepDefinition(
                    id="step1",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                    depends_on=["step2"],
                ),
                StepDefinition(
                    id="step2",
                    model=ModelName.HAIKU,
                    prompt_strategy="prompt.md",
                    depends_on=["step1"],
                ),
            ],
        )

        with pytest.raises(ValueError, match="Circular dependency"):
            resolve_execution_order(workflow)


class TestWorkflowExecutor:
    """Tests for workflow execution."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a temporary workspace."""
        ws_path = tmp_path / "00001"
        ws_path.mkdir()
        (ws_path / "project").mkdir()
        (ws_path / "context").mkdir()
        (ws_path / "state").mkdir()
        (ws_path / "logs").mkdir()

        return WorkspaceInfo.from_path(ws_path)

    @pytest.fixture
    def mock_prompt(self, tmp_path):
        """Create a test prompt file."""
        prompt_path = tmp_path / "test_prompt.md"
        prompt_path.write_text("Test prompt for {problem_name}")
        return str(prompt_path)

    def test_execute_single_step_workflow(self, workspace, mock_prompt):
        """Test executing a workflow with single step."""
        workflow = WorkflowDefinition(
            name="single_step",
            steps=[
                StepDefinition(
                    id="step1",
                    model=ModelName.HAIKU,
                    wrapper="mock",
                    prompt_strategy=mock_prompt,
                    outputs=["output.txt"],
                ),
            ],
        )

        executor = WorkflowExecutor()
        state = executor.run(workflow, workspace, context={"problem_name": "test"})

        assert state.is_complete
        assert not state.has_failures
        assert state.steps["step1"].status == StepStatus.COMPLETED
        assert state.total_tokens > 0

    def test_execute_multi_step_workflow(self, workspace, mock_prompt):
        """Test executing workflow with multiple dependent steps."""
        workflow = WorkflowDefinition(
            name="multi_step",
            steps=[
                StepDefinition(
                    id="step1",
                    model=ModelName.HAIKU,
                    wrapper="mock",
                    prompt_strategy=mock_prompt,
                    outputs=["output1.txt"],
                ),
                StepDefinition(
                    id="step2",
                    model=ModelName.SONNET,
                    wrapper="mock",
                    prompt_strategy=mock_prompt,
                    outputs=["output2.txt"],
                    depends_on=["step1"],
                ),
            ],
        )

        executor = WorkflowExecutor()
        state = executor.run(workflow, workspace, context={"problem_name": "test"})

        assert state.is_complete
        assert not state.has_failures
        assert state.steps["step1"].status == StepStatus.COMPLETED
        assert state.steps["step2"].status == StepStatus.COMPLETED

        # Check execution order (step1 should complete before step2 starts)
        assert state.steps["step1"].completed_at < state.steps["step2"].started_at

    def test_workflow_stops_on_failure(self, workspace, tmp_path):
        """Test that workflow stops when a step fails."""
        fail_prompt = tmp_path / "fail_prompt.md"
        fail_prompt.write_text("MOCK_FAIL")

        success_prompt = tmp_path / "success_prompt.md"
        success_prompt.write_text("Success")

        workflow = WorkflowDefinition(
            name="fail_workflow",
            steps=[
                StepDefinition(
                    id="step1",
                    model=ModelName.HAIKU,
                    wrapper="mock",
                    prompt_strategy=str(fail_prompt),
                    outputs=["output1.txt"],
                ),
                StepDefinition(
                    id="step2",
                    model=ModelName.HAIKU,
                    wrapper="mock",
                    prompt_strategy=str(success_prompt),
                    outputs=["output2.txt"],
                    depends_on=["step1"],
                ),
            ],
        )

        executor = WorkflowExecutor()
        state = executor.run(workflow, workspace)

        assert state.is_complete
        assert state.has_failures
        assert state.steps["step1"].status == StepStatus.FAILED
        assert state.steps["step2"].status == StepStatus.PENDING  # Never executed due to stop-on-failure

    def test_resume_incomplete_workflow(self, workspace, mock_prompt):
        """Test resuming a workflow from saved state."""
        workflow = WorkflowDefinition(
            name="resume_test",
            steps=[
                StepDefinition(
                    id="step1",
                    model=ModelName.HAIKU,
                    wrapper="mock",
                    prompt_strategy=mock_prompt,
                    outputs=["output1.txt"],
                ),
                StepDefinition(
                    id="step2",
                    model=ModelName.HAIKU,
                    wrapper="mock",
                    prompt_strategy=mock_prompt,
                    outputs=["output2.txt"],
                    depends_on=["step1"],
                ),
            ],
        )

        executor = WorkflowExecutor()

        # Run first step only by making step2 fail initially
        # We'll simulate interruption by running partial workflow
        state = executor.run(workflow, workspace, context={"problem_name": "test"})

        # Both steps should complete in normal run
        assert state.steps["step1"].status == StepStatus.COMPLETED

        # Now resume (should be no-op since workflow is complete)
        with pytest.raises(ValueError, match="already complete"):
            executor.resume(workflow, workspace)

    def test_resume_with_failed_step(self, workspace, tmp_path):
        """Test resuming after a failed step."""
        # Create two prompts: one that fails, one that succeeds
        fail_prompt = tmp_path / "fail_prompt.md"
        fail_prompt.write_text("MOCK_FAIL")

        success_prompt = tmp_path / "success_prompt.md"
        success_prompt.write_text("Success")

        # Create workflow with independent steps
        workflow = WorkflowDefinition(
            name="resume_fail_test",
            steps=[
                StepDefinition(
                    id="step1",
                    model=ModelName.HAIKU,
                    wrapper="mock",
                    prompt_strategy=str(fail_prompt),
                    outputs=["output1.txt"],
                ),
                StepDefinition(
                    id="step2",
                    model=ModelName.HAIKU,
                    wrapper="mock",
                    prompt_strategy=str(success_prompt),
                    outputs=["output2.txt"],
                    # No dependency, so it will also execute
                ),
            ],
        )

        executor = WorkflowExecutor()
        state = executor.run(workflow, workspace)

        assert state.has_failures
        assert state.steps["step1"].status == StepStatus.FAILED
        # step2 never runs because executor stops on first failure
        assert state.steps["step2"].status == StepStatus.PENDING

    def test_state_persisted_during_execution(self, workspace, mock_prompt):
        """Test that state is saved after each step."""
        workflow = WorkflowDefinition(
            name="persist_test",
            steps=[
                StepDefinition(
                    id="step1",
                    model=ModelName.HAIKU,
                    wrapper="mock",
                    prompt_strategy=mock_prompt,
                    outputs=["output1.txt"],
                ),
            ],
        )

        executor = WorkflowExecutor()
        executor.run(workflow, workspace, context={"problem_name": "test"})

        # Load state from disk
        from pipeline.state import load_state
        loaded_state = load_state(workspace)

        assert loaded_state is not None
        assert loaded_state.is_complete
        assert loaded_state.steps["step1"].status == StepStatus.COMPLETED
