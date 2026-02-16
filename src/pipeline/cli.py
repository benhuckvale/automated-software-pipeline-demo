"""Command-line interface for the pipeline."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import structlog

from . import configure_logging
from .executor import WorkflowExecutor
from .parser import parse_workflow, validate_workflow
from .workspace import create_workspace, get_workspace, list_workspaces
from .state import load_state, get_state_summary, can_resume

logger = structlog.get_logger()


def cmd_run(args):
    """Run a new workflow execution."""
    workflow_path = Path(args.workflow)
    problem_path = Path(args.problem) if args.problem else None

    # Validate inputs
    if not workflow_path.exists():
        print(f"Error: Workflow file not found: {workflow_path}", file=sys.stderr)
        return 1

    if problem_path and not problem_path.exists():
        print(f"Error: Problem file not found: {problem_path}", file=sys.stderr)
        return 1

    # Parse workflow
    try:
        workflow = parse_workflow(workflow_path)
        print(f"✓ Loaded workflow: {workflow.name}")
        print(f"  Steps: {len(workflow.steps)}")

        # Validate
        valid, errors = validate_workflow(workflow)
        if not valid:
            print("✗ Workflow validation failed:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1

    except Exception as e:
        print(f"Error parsing workflow: {e}", file=sys.stderr)
        return 1

    # Create workspace
    workspace = create_workspace()
    print(f"✓ Created workspace: {workspace.workspace_id}")
    print(f"  Path: {workspace.workspace_path}")

    # Configure logging to workspace
    log_file = workspace.logs_dir / "pipeline.log"
    # TODO: Configure file logging - for now using console

    # Build context
    context = {}
    if problem_path:
        context["problem_name"] = problem_path.stem

    # Execute workflow
    print(f"\n🚀 Starting workflow execution...\n")

    executor = WorkflowExecutor()

    try:
        state = executor.run(workflow, workspace, problem_path, context)

        # Print summary
        print(f"\n{'='*60}")
        if state.has_failures:
            print("✗ Workflow completed with failures")
        else:
            print("✓ Workflow completed successfully")

        print(f"\nWorkspace: {workspace.workspace_id}")
        print(f"Steps completed: {len(state.completed_steps)}/{len(workflow.steps)}")
        print(f"Total tokens: {state.total_tokens}")
        print(f"Duration: {(state.completed_at - state.started_at).total_seconds():.1f}s")

        # Show step statuses
        print(f"\nStep Status:")
        for step_id, result in state.steps.items():
            status_icon = "✓" if result.status.value == "completed" else "✗"
            print(f"  {status_icon} {step_id}: {result.status.value}")
            if result.error:
                print(f"      Error: {result.error}")

        print(f"{'='*60}\n")

        return 0 if not state.has_failures else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user", file=sys.stderr)
        print(f"   Resume with: pipeline resume --workspace {workspace.workspace_id}\n")
        return 130

    except Exception as e:
        print(f"\n✗ Workflow execution failed: {e}", file=sys.stderr)
        logger.exception("workflow_execution_failed")
        return 1


def cmd_resume(args):
    """Resume a workflow execution from saved state."""
    workspace_id = args.workspace

    try:
        workspace = get_workspace(workspace_id)
    except FileNotFoundError:
        print(f"Error: Workspace {workspace_id} not found", file=sys.stderr)
        return 1

    # Check if can resume
    if not can_resume(workspace):
        print(f"Error: Workspace {workspace_id} has no resumable state", file=sys.stderr)
        print("  (either no state found or workflow already complete)")
        return 1

    # Load state
    state = load_state(workspace)
    print(f"✓ Loaded workspace: {workspace_id}")
    print(f"  Workflow: {state.workflow_name}")
    print(f"  Completed steps: {len(state.completed_steps)}")
    print(f"  Pending steps: {len(state.pending_steps)}")

    # Load workflow definition
    # Note: We need to know which workflow file to use
    # For now, assume standard path - in production, store this in state
    workflow_path = Path(f"workflows/{state.workflow_name}.yaml")

    if not workflow_path.exists():
        # Try to find workflow by searching
        workflow_dir = Path("workflows")
        candidates = list(workflow_dir.glob("*.yaml"))

        if not candidates:
            print(f"Error: Could not find workflow file for {state.workflow_name}", file=sys.stderr)
            print(f"  Searched in: {workflow_dir}", file=sys.stderr)
            return 1

        if len(candidates) == 1:
            workflow_path = candidates[0]
        else:
            print(f"Error: Multiple workflow files found, please specify with --workflow", file=sys.stderr)
            return 1

    try:
        workflow = parse_workflow(workflow_path)
    except Exception as e:
        print(f"Error parsing workflow: {e}", file=sys.stderr)
        return 1

    # Resume execution
    print(f"\n🚀 Resuming workflow execution...\n")

    executor = WorkflowExecutor()

    try:
        state = executor.resume(workflow, workspace)

        # Print summary
        print(f"\n{'='*60}")
        if state.has_failures:
            print("✗ Workflow completed with failures")
        else:
            print("✓ Workflow completed successfully")

        print(f"\nWorkspace: {workspace_id}")
        print(f"Steps completed: {len(state.completed_steps)}/{len(workflow.steps)}")
        print(f"Total tokens: {state.total_tokens}")

        print(f"{'='*60}\n")

        return 0 if not state.has_failures else 1

    except Exception as e:
        print(f"\n✗ Workflow resume failed: {e}", file=sys.stderr)
        logger.exception("workflow_resume_failed")
        return 1


def cmd_status(args):
    """Show status of a workflow execution."""
    workspace_id = args.workspace

    try:
        workspace = get_workspace(workspace_id)
    except FileNotFoundError:
        print(f"Error: Workspace {workspace_id} not found", file=sys.stderr)
        return 1

    # Load state
    state = load_state(workspace)

    if state is None:
        print(f"Workspace: {workspace_id}")
        print("Status: No workflow state found")
        return 0

    # Get summary
    summary = get_state_summary(state)

    # Print formatted status
    print(f"\n{'='*60}")
    print(f"Workspace: {workspace_id}")
    print(f"Workflow: {state.workflow_name}")
    print(f"Status: {summary['status']}")
    print(f"{'='*60}")

    if summary['current_step']:
        print(f"\nCurrent step: {summary['current_step']}")

    print(f"\nCompleted steps: {len(summary['completed_steps'])}")
    for step_id in summary['completed_steps']:
        result = state.steps[step_id]
        print(f"  ✓ {step_id} ({result.tokens_used} tokens)")

    if summary['pending_steps']:
        print(f"\nPending steps: {len(summary['pending_steps'])}")
        for step_id in summary['pending_steps']:
            print(f"  - {step_id}")

    print(f"\nTotal tokens: {summary['total_tokens']}")

    if summary['duration_seconds']:
        print(f"Duration: {summary['duration_seconds']:.1f}s")

    if summary['has_failures']:
        print(f"\n⚠️  Workflow has failures")

    print(f"{'='*60}\n")

    return 0


def cmd_list(args):
    """List all workspaces."""
    workspaces = list_workspaces()

    if not workspaces:
        print("No workspaces found")
        return 0

    print(f"\n{'='*60}")
    print(f"Workspaces ({len(workspaces)}):")
    print(f"{'='*60}\n")

    for ws in workspaces:
        state = load_state(ws)
        if state:
            status = "✓ complete" if state.is_complete else "⏳ in progress"
            if state.has_failures:
                status = "✗ failed"

            print(f"{ws.workspace_id}: {state.workflow_name} - {status}")
        else:
            print(f"{ws.workspace_id}: (no state)")

    print()
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Automated software delivery pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a workflow")
    run_parser.add_argument(
        "--workflow",
        required=True,
        help="Path to workflow YAML file",
    )
    run_parser.add_argument(
        "--problem",
        help="Path to problem description file",
    )

    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume a workflow")
    resume_parser.add_argument(
        "--workspace",
        required=True,
        help="Workspace ID to resume",
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show workflow status")
    status_parser.add_argument(
        "--workspace",
        required=True,
        help="Workspace ID to check",
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List all workspaces")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Configure logging
    configure_logging()

    # Route to command handler
    commands = {
        "run": cmd_run,
        "resume": cmd_resume,
        "status": cmd_status,
        "list": cmd_list,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
