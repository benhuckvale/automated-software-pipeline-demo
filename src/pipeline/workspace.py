"""Workspace management for pipeline executions."""
import shutil
from datetime import datetime
from pathlib import Path

import structlog

from .models import WorkspaceInfo

logger = structlog.get_logger()

# Default base directory for all workspaces
WORKSPACES_BASE = Path("workspaces")


def get_next_build_number(base_dir: Path = WORKSPACES_BASE) -> int:
    """Get the next available build number.

    Args:
        base_dir: Base directory containing workspace directories

    Returns:
        Next build number (1 if no workspaces exist)
    """
    if not base_dir.exists():
        return 1

    existing = [
        int(p.name) for p in base_dir.iterdir()
        if p.is_dir() and p.name.isdigit()
    ]

    return max(existing, default=0) + 1


def create_workspace(
    build_number: int | None = None,
    base_dir: Path = WORKSPACES_BASE,
) -> WorkspaceInfo:
    """Create a new workspace directory structure.

    Args:
        build_number: Optional build number (auto-generated if None)
        base_dir: Base directory for workspaces

    Returns:
        WorkspaceInfo with paths to all workspace directories

    Directory structure:
        workspaces/
          {build_number:05d}/
            project/        # Working directory for code
            context/        # Problem descriptions, clarifications
            state/          # Workflow state files
            logs/           # Execution logs
    """
    if build_number is None:
        build_number = get_next_build_number(base_dir)

    workspace_id = f"{build_number:05d}"
    workspace_path = base_dir / workspace_id

    if workspace_path.exists():
        raise ValueError(f"Workspace {workspace_id} already exists")

    # Create directory structure
    workspace_path.mkdir(parents=True)
    (workspace_path / "project").mkdir()
    (workspace_path / "context").mkdir()
    (workspace_path / "state").mkdir()
    (workspace_path / "logs").mkdir()

    logger.info("workspace_created", workspace_id=workspace_id, path=str(workspace_path))

    return WorkspaceInfo.from_path(workspace_path)


def get_workspace(workspace_id: str, base_dir: Path = WORKSPACES_BASE) -> WorkspaceInfo:
    """Get information about an existing workspace.

    Args:
        workspace_id: Workspace ID (e.g., "00001")
        base_dir: Base directory for workspaces

    Returns:
        WorkspaceInfo for the workspace

    Raises:
        FileNotFoundError: If workspace doesn't exist
    """
    workspace_path = base_dir / workspace_id

    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace {workspace_id} not found")

    return WorkspaceInfo.from_path(workspace_path)


def list_workspaces(base_dir: Path = WORKSPACES_BASE) -> list[WorkspaceInfo]:
    """List all existing workspaces.

    Args:
        base_dir: Base directory for workspaces

    Returns:
        List of WorkspaceInfo, sorted by creation time (newest first)
    """
    if not base_dir.exists():
        return []

    workspaces = [
        WorkspaceInfo.from_path(p)
        for p in base_dir.iterdir()
        if p.is_dir() and p.name.isdigit()
    ]

    return sorted(workspaces, key=lambda w: w.created_at, reverse=True)


def delete_workspace(workspace_id: str, base_dir: Path = WORKSPACES_BASE):
    """Delete a workspace and all its contents.

    Args:
        workspace_id: Workspace ID to delete
        base_dir: Base directory for workspaces

    Raises:
        FileNotFoundError: If workspace doesn't exist
    """
    workspace_path = base_dir / workspace_id

    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace {workspace_id} not found")

    shutil.rmtree(workspace_path)
    logger.info("workspace_deleted", workspace_id=workspace_id)


def copy_file_to_context(
    source_path: Path,
    workspace: WorkspaceInfo,
    dest_name: str | None = None,
) -> Path:
    """Copy a file into the workspace context directory.

    Args:
        source_path: Path to source file
        workspace: Target workspace
        dest_name: Optional destination filename (defaults to source filename)

    Returns:
        Path to the copied file in the context directory
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    dest_name = dest_name or source_path.name
    dest_path = workspace.context_dir / dest_name

    shutil.copy2(source_path, dest_path)
    logger.debug("file_copied_to_context", source=str(source_path), dest=str(dest_path))

    return dest_path
