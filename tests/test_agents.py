"""Tests for agent executors."""
import pytest
from pathlib import Path

from pipeline.agents.mock import MockAgentExecutor
from pipeline.models import StepDefinition, ModelName
from pipeline.workspace import create_workspace


class TestMockAgentExecutor:
    """Tests for MockAgentExecutor."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a temporary workspace for testing."""
        from pipeline.models import WorkspaceInfo
        from datetime import datetime

        # Create workspace structure in tmp directory
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
        prompt_path.write_text("""# Test Prompt

Workspace: {workspace}
Problem: {problem_name}

Generate test outputs.
""")
        return str(prompt_path)

    def test_mock_executor_success(self, workspace, mock_prompt):
        """Test successful mock execution."""
        step = StepDefinition(
            id="test_step",
            model=ModelName.HAIKU,
            prompt_strategy=mock_prompt,
            outputs=["context/output.md", "project/solution.py"],
        )

        executor = MockAgentExecutor()
        result = executor.execute_step(
            step, workspace, {"problem_name": "test_problem"}
        )

        assert result.status.value == "completed"
        assert result.tokens_used > 0
        assert len(result.outputs) == 2
        assert "context/output.md" in result.outputs
        assert "project/solution.py" in result.outputs

        # Verify files were created
        assert (workspace.workspace_path / "context/output.md").exists()
        assert (workspace.workspace_path / "project/solution.py").exists()

    def test_mock_executor_fail_directive(self, workspace, tmp_path):
        """Test mock failure via MOCK_FAIL directive."""
        prompt_path = tmp_path / "fail_prompt.md"
        prompt_path.write_text("# Fail Test\n\nMOCK_FAIL")

        step = StepDefinition(
            id="fail_step",
            model=ModelName.HAIKU,
            prompt_strategy=str(prompt_path),
            outputs=["output.txt"],
        )

        executor = MockAgentExecutor()
        result = executor.execute_step(step, workspace)

        assert result.status.value == "failed"
        assert "Mock failure" in result.error

    def test_mock_executor_slow_directive(self, workspace, tmp_path):
        """Test mock delay via MOCK_SLOW directive."""
        prompt_path = tmp_path / "slow_prompt.md"
        prompt_path.write_text("# Slow Test\n\nMOCK_SLOW\nGenerate outputs.")

        step = StepDefinition(
            id="slow_step",
            model=ModelName.HAIKU,
            prompt_strategy=str(prompt_path),
            outputs=["output.txt"],
        )

        executor = MockAgentExecutor()

        import time
        start = time.time()
        result = executor.execute_step(step, workspace)
        duration = time.time() - start

        # Should take at least 2 seconds due to MOCK_SLOW
        assert duration >= 2.0
        assert result.status.value == "completed"  # MOCK_SLOW adds delay but succeeds

    def test_mock_generates_correct_python_content(self, workspace, mock_prompt):
        """Test that mock generates valid Python code."""
        step = StepDefinition(
            id="code_step",
            model=ModelName.SONNET,
            prompt_strategy=mock_prompt,
            outputs=["project/solution.py"],
        )

        executor = MockAgentExecutor()
        result = executor.execute_step(
            step, workspace, {"problem_name": "reverse_string"}
        )

        assert result.status.value == "completed"

        # Check Python file was created with valid content
        py_file = workspace.workspace_path / "project/solution.py"
        assert py_file.exists()

        content = py_file.read_text()
        assert "def solution(" in content
        assert "reverse_string" in content

    def test_mock_generates_markdown_content(self, workspace, mock_prompt):
        """Test that mock generates markdown documents."""
        step = StepDefinition(
            id="analysis_step",
            model=ModelName.HAIKU,
            prompt_strategy=mock_prompt,
            outputs=["context/analysis.md"],
        )

        executor = MockAgentExecutor()
        result = executor.execute_step(
            step, workspace, {"problem_name": "two_sum"}
        )

        assert result.status.value == "completed"

        # Check markdown file was created
        md_file = workspace.workspace_path / "context/analysis.md"
        assert md_file.exists()

        content = md_file.read_text()
        assert "# Mock Output" in content
        assert "two_sum" in content
