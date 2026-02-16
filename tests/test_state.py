"""Tests for state persistence."""
import pytest
from datetime import datetime

from pipeline.state import save_state, load_state, can_resume, get_state_summary
from pipeline.models import WorkflowState, StepResult, StepStatus, WorkspaceInfo


class TestStatePersistence:
    """Tests for workflow state persistence."""

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
    def sample_state(self, workspace):
        """Create a sample workflow state."""
        return WorkflowState(
            workflow_id=workspace.workspace_id,
            workflow_name="test_workflow",
            workspace_path=str(workspace.workspace_path),
            started_at=datetime.now(),
        )

    def test_save_and_load_state(self, workspace, sample_state):
        """Test saving and loading state."""
        save_state(sample_state, workspace)

        loaded = load_state(workspace)

        assert loaded is not None
        assert loaded.workflow_id == sample_state.workflow_id
        assert loaded.workflow_name == sample_state.workflow_name

    def test_load_nonexistent_state(self, workspace):
        """Test loading state when file doesn't exist."""
        loaded = load_state(workspace)
        assert loaded is None

    def test_can_resume_incomplete_workflow(self, workspace, sample_state):
        """Test resume detection for incomplete workflow."""
        save_state(sample_state, workspace)

        assert can_resume(workspace) is True

    def test_can_resume_completed_workflow(self, workspace, sample_state):
        """Test resume detection for completed workflow."""
        sample_state.completed_at = datetime.now()
        save_state(sample_state, workspace)

        assert can_resume(workspace) is False

    def test_can_resume_no_state(self, workspace):
        """Test resume detection with no state file."""
        assert can_resume(workspace) is False

    def test_state_with_step_results(self, workspace, sample_state):
        """Test state persistence with step results."""
        # Add step results
        result1 = StepResult(
            step_id="step1",
            status=StepStatus.COMPLETED,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            tokens_used=100,
        )

        result2 = StepResult(
            step_id="step2",
            status=StepStatus.IN_PROGRESS,
            started_at=datetime.now(),
            tokens_used=50,
        )

        sample_state.update_step(result1)
        sample_state.update_step(result2)

        save_state(sample_state, workspace)
        loaded = load_state(workspace)

        assert len(loaded.steps) == 2
        assert loaded.steps["step1"].status == StepStatus.COMPLETED
        assert loaded.steps["step2"].status == StepStatus.IN_PROGRESS
        assert loaded.current_step == "step2"
        assert loaded.total_tokens == 150

    def test_get_state_summary(self, sample_state):
        """Test state summary generation."""
        summary = get_state_summary(sample_state)

        assert summary["workflow_id"] == sample_state.workflow_id
        assert summary["workflow_name"] == sample_state.workflow_name
        assert summary["status"] == "in_progress"
        assert summary["has_failures"] is False
        assert summary["total_tokens"] == 0
        assert "duration_seconds" in summary
