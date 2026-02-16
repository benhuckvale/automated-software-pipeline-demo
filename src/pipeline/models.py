"""Pydantic models for workflow definitions and runtime state."""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ModelName(str, Enum):
    """Supported Claude model names."""
    HAIKU = "haiku"
    SONNET = "sonnet"
    OPUS = "opus"


class StepStatus(str, Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepDefinition(BaseModel):
    """Definition of a single workflow step from YAML."""
    id: str = Field(..., description="Unique step identifier")
    model: ModelName = Field(..., description="Claude model to use")
    wrapper: str = Field(default="claude_code", description="Agent wrapper type")
    prompt_strategy: str = Field(..., description="Path to prompt template file")
    outputs: list[str] = Field(default_factory=list, description="Expected output files (workspace-relative)")
    depends_on: list[str] = Field(default_factory=list, description="Step IDs this step depends on")
    timeout: int = Field(default=300, description="Timeout in seconds")
    max_turns: int = Field(default=10, description="Max agent turns")

    @field_validator("outputs")
    @classmethod
    def validate_outputs(cls, v: list[str]) -> list[str]:
        """Ensure output paths don't start with /."""
        for path in v:
            if path.startswith("/"):
                raise ValueError(f"Output path must be relative: {path}")
        return v


class WorkflowDefinition(BaseModel):
    """Complete workflow definition parsed from YAML."""
    name: str = Field(..., description="Workflow name")
    description: str = Field(default="", description="Workflow description")
    steps: list[StepDefinition] = Field(..., description="Workflow steps")

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, v: list[StepDefinition]) -> list[StepDefinition]:
        """Validate step IDs are unique and dependencies exist."""
        step_ids = {step.id for step in v}
        if len(step_ids) != len(v):
            raise ValueError("Duplicate step IDs found")

        for step in v:
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise ValueError(f"Step '{step.id}' depends on non-existent step '{dep}'")

        return v


class StepResult(BaseModel):
    """Result from executing a workflow step."""
    step_id: str
    status: StepStatus
    started_at: datetime
    completed_at: datetime | None = None
    outputs: dict[str, str] = Field(default_factory=dict, description="Output file paths and content hashes")
    tokens_used: int = Field(default=0)
    error: str | None = None
    agent_output: str | None = Field(default=None, description="Raw agent output for debugging")

    @property
    def duration_seconds(self) -> float | None:
        """Calculate step duration."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class WorkflowState(BaseModel):
    """Runtime state of a workflow execution."""
    workflow_id: str = Field(..., description="Unique workflow execution ID (build number)")
    workflow_name: str
    workspace_path: str
    problem_file: str | None = None

    started_at: datetime
    completed_at: datetime | None = None

    steps: dict[str, StepResult] = Field(default_factory=dict, description="Step ID -> Result mapping")
    current_step: str | None = None

    total_tokens: int = 0

    @property
    def is_complete(self) -> bool:
        """Check if workflow is complete (all steps completed or failed)."""
        return self.completed_at is not None

    @property
    def has_failures(self) -> bool:
        """Check if any steps failed."""
        return any(result.status == StepStatus.FAILED for result in self.steps.values())

    @property
    def completed_steps(self) -> list[str]:
        """Get list of completed step IDs."""
        return [
            step_id for step_id, result in self.steps.items()
            if result.status == StepStatus.COMPLETED
        ]

    @property
    def pending_steps(self) -> list[str]:
        """Get list of pending step IDs (not started yet)."""
        return [
            step_id for step_id, result in self.steps.items()
            if result.status == StepStatus.PENDING
        ]

    def get_step_result(self, step_id: str) -> StepResult | None:
        """Get result for a specific step."""
        return self.steps.get(step_id)

    def update_step(self, result: StepResult):
        """Update or add a step result."""
        self.steps[result.step_id] = result
        if result.status == StepStatus.IN_PROGRESS:
            self.current_step = result.step_id
        elif result.status in [StepStatus.COMPLETED, StepStatus.FAILED]:
            if self.current_step == result.step_id:
                self.current_step = None

        # Update token count
        self.total_tokens += result.tokens_used


class WorkspaceInfo(BaseModel):
    """Metadata about a workspace."""
    workspace_id: str
    workspace_path: Path
    created_at: datetime

    # Directory structure
    project_dir: Path
    context_dir: Path
    state_dir: Path
    logs_dir: Path

    @classmethod
    def from_path(cls, workspace_path: Path) -> "WorkspaceInfo":
        """Create WorkspaceInfo from a workspace path."""
        return cls(
            workspace_id=workspace_path.name,
            workspace_path=workspace_path,
            created_at=datetime.fromtimestamp(workspace_path.stat().st_ctime),
            project_dir=workspace_path / "project",
            context_dir=workspace_path / "context",
            state_dir=workspace_path / "state",
            logs_dir=workspace_path / "logs",
        )
