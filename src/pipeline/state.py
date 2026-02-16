"""State persistence for workflow executions."""
import json
from pathlib import Path
from typing import Any

import structlog

from .models import WorkflowState, WorkspaceInfo

logger = structlog.get_logger()

STATE_FILENAME = "workflow_state.json"


def save_state(state: WorkflowState, workspace: WorkspaceInfo):
    """Save workflow state to disk with atomic write.

    Args:
        state: Workflow state to save
        workspace: Workspace containing state directory

    The state is written to a temporary file first, then atomically renamed
    to ensure we never have a partially written state file.
    """
    state_path = workspace.state_dir / STATE_FILENAME
    temp_path = workspace.state_dir / f"{STATE_FILENAME}.tmp"

    # Serialize to JSON using Pydantic
    state_json = state.model_dump_json(indent=2)

    # Write to temp file
    temp_path.write_text(state_json)

    # Atomic rename
    temp_path.replace(state_path)

    logger.debug(
        "state_saved",
        workspace_id=workspace.workspace_id,
        current_step=state.current_step,
        completed_steps=len(state.completed_steps),
    )


def load_state(workspace: WorkspaceInfo) -> WorkflowState | None:
    """Load workflow state from disk.

    Args:
        workspace: Workspace to load state from

    Returns:
        WorkflowState if exists, None otherwise

    Raises:
        ValueError: If state file is corrupted or invalid
    """
    state_path = workspace.state_dir / STATE_FILENAME

    if not state_path.exists():
        logger.debug("no_state_found", workspace_id=workspace.workspace_id)
        return None

    try:
        state_json = state_path.read_text()
        state_dict = json.loads(state_json)
        state = WorkflowState(**state_dict)

        logger.debug(
            "state_loaded",
            workspace_id=workspace.workspace_id,
            current_step=state.current_step,
            completed_steps=len(state.completed_steps),
        )

        return state

    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Failed to load state from {state_path}: {e}")


def can_resume(workspace: WorkspaceInfo) -> bool:
    """Check if a workspace has a valid state that can be resumed.

    Args:
        workspace: Workspace to check

    Returns:
        True if workspace has a valid workflow state that can be resumed
        (either incomplete or complete with failures that can be retried)
    """
    try:
        state = load_state(workspace)
        if state is None:
            return False

        # Can resume if:
        # 1. Workflow is not complete yet, OR
        # 2. Workflow completed but has failures (allow retry)
        return not state.is_complete or state.has_failures

    except Exception as e:
        logger.warning("state_check_failed", workspace_id=workspace.workspace_id, error=str(e))
        return False


def create_backup(workspace: WorkspaceInfo) -> Path:
    """Create a backup of the current state file.

    Args:
        workspace: Workspace to backup

    Returns:
        Path to backup file

    Raises:
        FileNotFoundError: If no state file exists
    """
    state_path = workspace.state_dir / STATE_FILENAME

    if not state_path.exists():
        raise FileNotFoundError(f"No state file to backup in {workspace.workspace_id}")

    # Create backup with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = workspace.state_dir / f"workflow_state_{timestamp}.json.bak"

    import shutil
    shutil.copy2(state_path, backup_path)

    logger.info("state_backup_created", workspace_id=workspace.workspace_id, backup=str(backup_path))

    return backup_path


def get_state_summary(state: WorkflowState) -> dict[str, Any]:
    """Get a summary of workflow state for display.

    Args:
        state: Workflow state

    Returns:
        Dictionary with human-readable summary
    """
    from datetime import datetime

    duration = None
    if state.completed_at:
        duration = (state.completed_at - state.started_at).total_seconds()
    elif state.started_at:
        duration = (datetime.now() - state.started_at).total_seconds()

    return {
        "workflow_id": state.workflow_id,
        "workflow_name": state.workflow_name,
        "status": "completed" if state.is_complete else "in_progress",
        "has_failures": state.has_failures,
        "current_step": state.current_step,
        "completed_steps": state.completed_steps,
        "pending_steps": state.pending_steps,
        "total_tokens": state.total_tokens,
        "duration_seconds": duration,
        "started_at": state.started_at.isoformat(),
        "completed_at": state.completed_at.isoformat() if state.completed_at else None,
    }
