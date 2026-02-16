"""YAML workflow parser."""
from pathlib import Path

import yaml
import structlog

from .models import WorkflowDefinition, StepDefinition

logger = structlog.get_logger()


def parse_workflow(yaml_path: str | Path) -> WorkflowDefinition:
    """Parse a workflow definition from YAML file.

    Args:
        yaml_path: Path to YAML workflow file

    Returns:
        Validated WorkflowDefinition

    Raises:
        FileNotFoundError: If YAML file doesn't exist
        ValueError: If YAML is invalid or validation fails
        yaml.YAMLError: If YAML syntax is invalid
    """
    yaml_path = Path(yaml_path)

    if not yaml_path.exists():
        raise FileNotFoundError(f"Workflow file not found: {yaml_path}")

    logger.debug("parsing_workflow", path=str(yaml_path))

    with open(yaml_path, "r") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}")

    if not isinstance(data, dict):
        raise ValueError("YAML must contain a dictionary at root level")

    if "workflow" not in data:
        raise ValueError("YAML must contain 'workflow' key")

    workflow_data = data["workflow"]

    # Parse workflow definition using Pydantic
    try:
        workflow = WorkflowDefinition(**workflow_data)
    except Exception as e:
        raise ValueError(f"Workflow validation failed: {e}")

    logger.info(
        "workflow_parsed",
        name=workflow.name,
        steps=len(workflow.steps),
        path=str(yaml_path),
    )

    return workflow


def detect_cycles(workflow: WorkflowDefinition) -> list[str] | None:
    """Detect circular dependencies in workflow steps.

    Args:
        workflow: Workflow to check

    Returns:
        List of step IDs forming a cycle, or None if no cycles exist
    """
    # Build adjacency list
    graph: dict[str, list[str]] = {step.id: step.depends_on for step in workflow.steps}

    # Track visited nodes and recursion stack
    visited: set[str] = set()
    rec_stack: set[str] = set()
    path: list[str] = []

    def dfs(node: str) -> list[str] | None:
        """DFS to detect cycles."""
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                cycle = dfs(neighbor)
                if cycle:
                    return cycle
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                return path[cycle_start:] + [neighbor]

        path.pop()
        rec_stack.remove(node)
        return None

    # Check all nodes
    for step_id in graph:
        if step_id not in visited:
            cycle = dfs(step_id)
            if cycle:
                return cycle

    return None


def validate_workflow(workflow: WorkflowDefinition) -> tuple[bool, list[str]]:
    """Validate workflow definition.

    Args:
        workflow: Workflow to validate

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    # Check for cycles
    cycle = detect_cycles(workflow)
    if cycle:
        errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")

    # Validate prompt files exist
    for step in workflow.steps:
        prompt_path = Path(step.prompt_strategy)
        if not prompt_path.exists():
            errors.append(f"Prompt file not found for step '{step.id}': {prompt_path}")

    return len(errors) == 0, errors
