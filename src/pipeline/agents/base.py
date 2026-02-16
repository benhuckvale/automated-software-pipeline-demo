"""Base agent executor interface."""
from abc import ABC, abstractmethod
from datetime import datetime

import structlog

from ..models import StepDefinition, StepResult, StepStatus, WorkspaceInfo

logger = structlog.get_logger()


class AgentExecutor(ABC):
    """Abstract base class for agent executors.

    An agent executor is responsible for running a single workflow step
    using a specific execution strategy (real Claude API, mock, etc.).
    """

    def __init__(self, name: str):
        """Initialize the executor.

        Args:
            name: Human-readable name for this executor type
        """
        self.name = name

    @abstractmethod
    def execute_step(
        self,
        step: StepDefinition,
        workspace: WorkspaceInfo,
        context: dict[str, str] | None = None,
    ) -> StepResult:
        """Execute a workflow step.

        Args:
            step: Step definition from workflow
            workspace: Workspace containing all necessary directories
            context: Optional context variables for prompt substitution
                    (e.g., {"problem_name": "reverse_string"})

        Returns:
            StepResult with execution outcome

        The executor should:
        1. Load the prompt template from step.prompt_strategy
        2. Substitute context variables (e.g., {workspace}, {problem_name})
        3. Execute the agent (real or mock)
        4. Validate expected outputs exist
        5. Return StepResult with status and metadata
        """
        pass

    def validate_outputs(
        self,
        step: StepDefinition,
        workspace: WorkspaceInfo,
    ) -> tuple[bool, list[str]]:
        """Validate that expected output files exist.

        Args:
            step: Step definition with expected outputs
            workspace: Workspace to check

        Returns:
            Tuple of (all_exist, list of missing files)
        """
        missing = []

        for output_path in step.outputs:
            # Output paths are workspace-relative
            full_path = workspace.workspace_path / output_path

            if not full_path.exists():
                missing.append(output_path)
            elif full_path.is_file() and full_path.stat().st_size == 0:
                # Warn about empty files but don't fail
                logger.warning(
                    "output_file_empty",
                    step_id=step.id,
                    file=output_path,
                )

        return len(missing) == 0, missing

    def load_prompt_template(
        self,
        prompt_path: str,
        context: dict[str, str] | None = None,
    ) -> str:
        """Load and substitute prompt template.

        Args:
            prompt_path: Path to prompt template file
            context: Variables to substitute (e.g., {workspace} -> /path/to/ws)

        Returns:
            Prompt text with variables substituted

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        from pathlib import Path

        prompt_file = Path(prompt_path)

        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

        prompt_text = prompt_file.read_text()

        # Substitute context variables
        if context:
            for key, value in context.items():
                prompt_text = prompt_text.replace(f"{{{key}}}", value)

        return prompt_text
