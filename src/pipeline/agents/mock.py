"""Mock agent executor for testing without real Claude inference."""
import time
from datetime import datetime
from pathlib import Path

import structlog

from ..models import StepDefinition, StepResult, StepStatus, WorkspaceInfo
from .base import AgentExecutor

logger = structlog.get_logger()


class MockAgentExecutor(AgentExecutor):
    """Mock executor that simulates agent behavior without real inference.

    This executor is used for testing the pipeline infrastructure without
    making actual API calls. It writes predetermined outputs based on the
    step configuration.

    Mock behavior can be controlled via the step's prompt_strategy path:
    - If prompt contains "MOCK_FAIL", the step will fail
    - If prompt contains "MOCK_SLOW", adds a 2-second delay
    - Otherwise, writes success outputs based on step.outputs
    """

    def __init__(self):
        super().__init__(name="mock")

    def execute_step(
        self,
        step: StepDefinition,
        workspace: WorkspaceInfo,
        context: dict[str, str] | None = None,
    ) -> StepResult:
        """Execute a mock step with predetermined behavior.

        Args:
            step: Step definition
            workspace: Workspace info
            context: Optional context variables

        Returns:
            StepResult with mock execution outcome
        """
        started_at = datetime.now()
        context = context or {}

        logger.info(
            "mock_step_started",
            step_id=step.id,
            workspace_id=workspace.workspace_id,
        )

        try:
            # Load prompt to check for mock directives
            prompt_text = self.load_prompt_template(step.prompt_strategy, context)

            # Check for mock directives
            should_fail = "MOCK_FAIL" in prompt_text
            should_slow = "MOCK_SLOW" in prompt_text

            if should_slow:
                logger.debug("mock_delay", step_id=step.id, seconds=2)
                time.sleep(2)

            if should_fail:
                logger.info("mock_step_failed", step_id=step.id)
                return StepResult(
                    step_id=step.id,
                    status=StepStatus.FAILED,
                    started_at=started_at,
                    completed_at=datetime.now(),
                    error="Mock failure triggered by MOCK_FAIL directive",
                    tokens_used=100,  # Mock token count
                )

            # Generate mock outputs
            outputs = self._generate_mock_outputs(step, workspace, context)

            # Validate outputs were created
            all_exist, missing = self.validate_outputs(step, workspace)

            if not all_exist:
                return StepResult(
                    step_id=step.id,
                    status=StepStatus.FAILED,
                    started_at=started_at,
                    completed_at=datetime.now(),
                    error=f"Mock failed to create outputs: {missing}",
                    tokens_used=50,
                )

            logger.info(
                "mock_step_completed",
                step_id=step.id,
                outputs=list(outputs.keys()),
            )

            return StepResult(
                step_id=step.id,
                status=StepStatus.COMPLETED,
                started_at=started_at,
                completed_at=datetime.now(),
                outputs=outputs,
                tokens_used=250,  # Mock token count
            )

        except Exception as e:
            logger.error(
                "mock_step_error",
                step_id=step.id,
                error=str(e),
            )

            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(),
                error=str(e),
                tokens_used=0,
            )

    def _generate_mock_outputs(
        self,
        step: StepDefinition,
        workspace: WorkspaceInfo,
        context: dict[str, str],
    ) -> dict[str, str]:
        """Generate mock output files.

        Args:
            step: Step definition
            workspace: Workspace info
            context: Context variables

        Returns:
            Dict mapping output paths to content hashes
        """
        outputs = {}

        for output_path in step.outputs:
            full_path = workspace.workspace_path / output_path

            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate mock content based on file type
            content = self._generate_mock_content(step, output_path, context)

            # Write mock file
            full_path.write_text(content)

            # Calculate simple hash (for tracking)
            import hashlib
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]

            outputs[output_path] = content_hash

            logger.debug(
                "mock_output_created",
                step_id=step.id,
                path=output_path,
                size=len(content),
            )

        return outputs

    def _generate_mock_content(
        self,
        step: StepDefinition,
        output_path: str,
        context: dict[str, str],
    ) -> str:
        """Generate mock content for an output file.

        Args:
            step: Step definition
            output_path: Relative path to output file
            context: Context variables

        Returns:
            Mock file content
        """
        problem_name = context.get("problem_name", "unknown")

        # Generate different content based on step ID and file type
        if output_path.endswith(".md"):
            return f"""# Mock Output: {step.id}

This is a mock output file generated for testing.

**Problem**: {problem_name}
**Step**: {step.id}
**Model**: {step.model.value}

Mock analysis and content go here.
"""

        elif output_path.endswith(".py"):
            # Generate mock Python code
            if "test" in step.id.lower():
                # Test step: generate test skeleton
                return f'''"""Mock tests for {problem_name}"""

def test_{problem_name}():
    """Mock test function."""
    # TODO: Implement actual tests
    assert True

def solution(input_data):
    """Placeholder solution function."""
    return input_data

if __name__ == "__main__":
    # Run tests
    test_{problem_name}()
    print("Mock tests passed!")
'''
            else:
                # Solution step: generate solution skeleton
                return f'''"""Mock solution for {problem_name}"""

def solution(input_data):
    """Mock solution implementation.

    Generated by step: {step.id}
    """
    # TODO: Implement actual solution
    return input_data

if __name__ == "__main__":
    # Mock test execution
    result = solution("test")
    print(f"Mock solution result: {{result}}")
'''

        else:
            # Generic text file
            return f"""Mock output for step: {step.id}
Problem: {problem_name}
Generated at: {datetime.now().isoformat()}

This is mock content for testing purposes.
"""
