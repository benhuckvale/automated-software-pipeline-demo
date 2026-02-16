"""Workflow orchestration and execution."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import structlog

from .models import (
    WorkflowDefinition,
    WorkflowState,
    StepResult,
    StepStatus,
    WorkspaceInfo,
)
from .state import save_state, load_state
from .agents.base import AgentExecutor
from .agents.mock import MockAgentExecutor
from .agents.claude_code import ClaudeCodeExecutor

logger = structlog.get_logger()


def resolve_execution_order(workflow: WorkflowDefinition) -> list[str]:
    """Resolve step execution order using topological sort.

    Args:
        workflow: Workflow definition

    Returns:
        List of step IDs in execution order

    Raises:
        ValueError: If circular dependency detected
    """
    from collections import deque

    # Build dependency graph
    in_degree = {step.id: 0 for step in workflow.steps}
    adjacency = {step.id: [] for step in workflow.steps}

    for step in workflow.steps:
        for dep in step.depends_on:
            adjacency[dep].append(step.id)
            in_degree[step.id] += 1

    # Kahn's algorithm for topological sort
    queue = deque([step_id for step_id, degree in in_degree.items() if degree == 0])
    result = []

    while queue:
        step_id = queue.popleft()
        result.append(step_id)

        for neighbor in adjacency[step_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check for cycles
    if len(result) != len(workflow.steps):
        missing = set(in_degree.keys()) - set(result)
        raise ValueError(f"Circular dependency detected involving steps: {missing}")

    logger.debug("execution_order_resolved", order=result)
    return result


class WorkflowExecutor:
    """Orchestrates workflow execution with state management."""

    def __init__(self):
        """Initialize executor with agent registry."""
        self._agents: dict[str, AgentExecutor] = {
            "mock": MockAgentExecutor(),
            "claude_code": ClaudeCodeExecutor(),
        }

    def register_agent(self, name: str, agent: AgentExecutor):
        """Register a custom agent executor.

        Args:
            name: Agent identifier
            agent: Agent executor instance
        """
        self._agents[name] = agent
        logger.debug("agent_registered", name=name)

    def run(
        self,
        workflow: WorkflowDefinition,
        workspace: WorkspaceInfo,
        problem_file: Path | None = None,
        context: dict[str, str] | None = None,
    ) -> WorkflowState:
        """Execute a workflow from start to finish.

        Args:
            workflow: Workflow definition
            workspace: Workspace for execution
            problem_file: Optional problem file to copy to context
            context: Optional context variables for prompt substitution

        Returns:
            Final workflow state
        """
        context = context or {}

        # Initialize state
        state = WorkflowState(
            workflow_id=workspace.workspace_id,
            workflow_name=workflow.name,
            workspace_path=str(workspace.workspace_path),
            started_at=datetime.now(),
            problem_file=str(problem_file) if problem_file else None,
        )

        # Copy problem file to context if provided
        if problem_file:
            from .workspace import copy_file_to_context
            copy_file_to_context(problem_file, workspace, "problem.txt")
            logger.info("problem_file_copied", source=str(problem_file))

        # Resolve execution order
        try:
            execution_order = resolve_execution_order(workflow)
        except ValueError as e:
            logger.error("workflow_validation_failed", error=str(e))
            raise

        logger.info(
            "workflow_started",
            workflow_id=state.workflow_id,
            workflow_name=workflow.name,
            steps=len(workflow.steps),
        )

        # Initialize step results as pending
        for step in workflow.steps:
            state.steps[step.id] = StepResult(
                step_id=step.id,
                status=StepStatus.PENDING,
                started_at=datetime.now(),  # Will be updated when actually started
            )

        save_state(state, workspace)

        # Execute steps in order
        step_map = {step.id: step for step in workflow.steps}

        for step_id in execution_order:
            step = step_map[step_id]

            # Check dependencies
            if not self._check_dependencies(step, state):
                logger.error(
                    "step_dependencies_failed",
                    step_id=step_id,
                    dependencies=step.depends_on,
                )
                result = StepResult(
                    step_id=step_id,
                    status=StepStatus.FAILED,
                    started_at=datetime.now(),
                    completed_at=datetime.now(),
                    error="Dependencies failed or incomplete",
                )
                state.update_step(result)
                save_state(state, workspace)
                continue

            # Execute step
            result = self._execute_step(step, workspace, context)
            state.update_step(result)
            save_state(state, workspace)

            # Stop on failure
            if result.status == StepStatus.FAILED:
                logger.error("workflow_stopped_on_failure", step_id=step_id)
                break

        # Mark workflow complete
        state.completed_at = datetime.now()
        save_state(state, workspace)

        logger.info(
            "workflow_completed",
            workflow_id=state.workflow_id,
            status="success" if not state.has_failures else "failed",
            total_tokens=state.total_tokens,
            duration=state.completed_at - state.started_at,
        )

        return state

    def resume(
        self,
        workflow: WorkflowDefinition,
        workspace: WorkspaceInfo,
        context: dict[str, str] | None = None,
    ) -> WorkflowState:
        """Resume a workflow from saved state.

        Args:
            workflow: Workflow definition
            workspace: Workspace with saved state
            context: Optional context variables

        Returns:
            Updated workflow state

        Raises:
            ValueError: If no state found or workflow already complete
        """
        context = context or {}

        # Load existing state
        state = load_state(workspace)

        if state is None:
            raise ValueError(f"No state found in workspace {workspace.workspace_id}")

        # Don't resume if successfully completed (no failures)
        if state.is_complete and not state.has_failures:
            raise ValueError(f"Workflow {state.workflow_id} is already complete with no failures")

        logger.info(
            "workflow_resumed",
            workflow_id=state.workflow_id,
            completed_steps=state.completed_steps,
        )

        # Reset completed_at if resuming a failed workflow
        if state.completed_at is not None:
            state.completed_at = None
            logger.debug("reset_completed_at", workflow_id=state.workflow_id)

        # Resolve execution order
        execution_order = resolve_execution_order(workflow)
        step_map = {step.id: step for step in workflow.steps}

        # Execute remaining steps
        for step_id in execution_order:
            # Skip completed steps
            step_result = state.get_step_result(step_id)
            if step_result and step_result.status == StepStatus.COMPLETED:
                logger.debug("step_already_completed", step_id=step_id)
                continue

            step = step_map[step_id]

            # Check dependencies
            if not self._check_dependencies(step, state):
                logger.error(
                    "step_dependencies_failed",
                    step_id=step_id,
                    dependencies=step.depends_on,
                )
                result = StepResult(
                    step_id=step_id,
                    status=StepStatus.FAILED,
                    started_at=datetime.now(),
                    completed_at=datetime.now(),
                    error="Dependencies failed or incomplete",
                )
                state.update_step(result)
                save_state(state, workspace)
                continue

            # Execute step
            result = self._execute_step(step, workspace, context)
            state.update_step(result)
            save_state(state, workspace)

            # Stop on failure
            if result.status == StepStatus.FAILED:
                logger.error("workflow_stopped_on_failure", step_id=step_id)
                break

        # Mark workflow complete
        state.completed_at = datetime.now()
        save_state(state, workspace)

        logger.info(
            "workflow_resume_completed",
            workflow_id=state.workflow_id,
            status="success" if not state.has_failures else "failed",
        )

        return state

    def _check_dependencies(
        self,
        step: StepDefinition,
        state: WorkflowState,
    ) -> bool:
        """Check if all step dependencies are satisfied.

        Args:
            step: Step to check
            state: Current workflow state

        Returns:
            True if all dependencies completed successfully
        """
        for dep_id in step.depends_on:
            dep_result = state.get_step_result(dep_id)

            if dep_result is None or dep_result.status != StepStatus.COMPLETED:
                logger.warning(
                    "dependency_not_satisfied",
                    step_id=step.id,
                    dependency=dep_id,
                    status=dep_result.status if dep_result else "not_started",
                )
                return False

        return True

    def _execute_step(
        self,
        step: StepDefinition,
        workspace: WorkspaceInfo,
        context: dict[str, str],
    ) -> StepResult:
        """Execute a single step using appropriate agent.

        Args:
            step: Step definition
            workspace: Workspace
            context: Context variables

        Returns:
            Step execution result
        """
        logger.info(
            "step_started",
            step_id=step.id,
            model=step.model.value,
            wrapper=step.wrapper,
        )

        # Get agent executor
        agent = self._agents.get(step.wrapper)

        if agent is None:
            logger.error("unknown_agent", wrapper=step.wrapper, step_id=step.id)
            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                error=f"Unknown agent wrapper: {step.wrapper}",
            )

        # Execute step
        try:
            result = agent.execute_step(step, workspace, context)
            return result

        except Exception as e:
            logger.error("step_execution_error", step_id=step.id, error=str(e))
            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                error=f"Execution error: {e}",
            )
