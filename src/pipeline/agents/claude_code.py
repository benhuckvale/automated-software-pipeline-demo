"""Claude Code agent executor using subprocess."""
import json
import subprocess
from datetime import datetime
from pathlib import Path

import structlog

from ..models import StepDefinition, StepResult, StepStatus, WorkspaceInfo, ModelName
from .base import AgentExecutor

logger = structlog.get_logger()

# Map our model names to Claude Code CLI model names
MODEL_MAP = {
    ModelName.HAIKU: "haiku",
    ModelName.SONNET: "sonnet",
    ModelName.OPUS: "opus",
}


class ClaudeCodeExecutor(AgentExecutor):
    """Executor that runs steps using Claude Code CLI via subprocess.

    This executor invokes the `claude` CLI tool with appropriate flags
    to run an agent in a sandboxed workspace environment.
    """

    def __init__(self):
        super().__init__(name="claude_code")

    def execute_step(
        self,
        step: StepDefinition,
        workspace: WorkspaceInfo,
        context: dict[str, str] | None = None,
    ) -> StepResult:
        """Execute a step using Claude Code CLI.

        Args:
            step: Step definition
            workspace: Workspace info
            context: Optional context variables for prompt substitution

        Returns:
            StepResult with execution outcome
        """
        started_at = datetime.now()
        context = context or {}

        # Add workspace path to context
        context["workspace"] = str(workspace.workspace_path)

        logger.info(
            "claude_code_step_started",
            step_id=step.id,
            model=step.model.value,
            workspace_id=workspace.workspace_id,
        )

        try:
            # Load and prepare prompt
            prompt_text = self.load_prompt_template(step.prompt_strategy, context)

            # Build Claude Code command
            cmd = self._build_command(step, workspace, prompt_text)

            logger.debug(
                "claude_code_command",
                step_id=step.id,
                cmd=" ".join(cmd),
            )

            # Execute with timeout
            result = subprocess.run(
                cmd,
                cwd=workspace.workspace_path,  # Run in workspace root
                capture_output=True,
                timeout=step.timeout,
                text=True,
            )

            completed_at = datetime.now()

            # Check exit code
            if result.returncode != 0:
                logger.error(
                    "claude_code_failed",
                    step_id=step.id,
                    exit_code=result.returncode,
                    stderr=result.stderr[:500],
                )

                return StepResult(
                    step_id=step.id,
                    status=StepStatus.FAILED,
                    started_at=started_at,
                    completed_at=completed_at,
                    error=f"Claude Code exited with code {result.returncode}: {result.stderr[:500]}",
                    agent_output=result.stdout,
                )

            # Parse output for token usage (if available)
            tokens_used = self._extract_token_usage(result.stdout)

            # Validate expected outputs
            all_exist, missing = self.validate_outputs(step, workspace)

            if not all_exist:
                logger.warning(
                    "claude_code_missing_outputs",
                    step_id=step.id,
                    missing=missing,
                )

                return StepResult(
                    step_id=step.id,
                    status=StepStatus.FAILED,
                    started_at=started_at,
                    completed_at=completed_at,
                    error=f"Expected outputs not created: {missing}",
                    tokens_used=tokens_used,
                    agent_output=result.stdout,
                )

            # Success!
            outputs = self._hash_outputs(step, workspace)

            logger.info(
                "claude_code_step_completed",
                step_id=step.id,
                tokens=tokens_used,
                outputs=list(outputs.keys()),
            )

            return StepResult(
                step_id=step.id,
                status=StepStatus.COMPLETED,
                started_at=started_at,
                completed_at=completed_at,
                outputs=outputs,
                tokens_used=tokens_used,
                agent_output=result.stdout,
            )

        except subprocess.TimeoutExpired:
            logger.error(
                "claude_code_timeout",
                step_id=step.id,
                timeout=step.timeout,
            )

            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(),
                error=f"Execution timed out after {step.timeout} seconds",
            )

        except Exception as e:
            logger.error(
                "claude_code_error",
                step_id=step.id,
                error=str(e),
            )

            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(),
                error=str(e),
            )

    def _build_command(
        self,
        step: StepDefinition,
        workspace: WorkspaceInfo,
        prompt_text: str,
    ) -> list[str]:
        """Build the Claude Code CLI command.

        Args:
            step: Step definition
            workspace: Workspace info
            prompt_text: Prepared prompt text

        Returns:
            Command as list of strings
        """
        model = MODEL_MAP.get(step.model, "sonnet")

        cmd = [
            "claude",
            "-p", prompt_text,
            "--model", model,
            "--max-turns", str(step.max_turns),
            "--add-dir", str(workspace.workspace_path),
            "--no-session-persistence",
        ]

        # Auto-approve common tools to avoid interactive prompts
        # Note: Only safe in controlled pipeline environment
        allowed_tools = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
        for tool in allowed_tools:
            cmd.extend(["--allowedTools", tool])

        # Auto-approve common tools to avoid interactive prompts
        # Note: This should be used carefully and only in controlled environments
        # For now, we'll rely on Claude Code's default permission handling
        # and let it prompt if needed (or use permission modes)

        return cmd

    def _extract_token_usage(self, output: str) -> int:
        """Extract token usage from Claude Code output.

        Args:
            output: stdout from Claude Code

        Returns:
            Token count, or 0 if not found
        """
        # Claude Code may output token usage in various formats
        # This is a simple parser - adjust based on actual output format
        try:
            # Look for patterns like "Tokens: 1234" or similar
            import re
            match = re.search(r"(\d+)\s+tokens?", output, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except Exception:
            pass

        return 0

    def _hash_outputs(
        self,
        step: StepDefinition,
        workspace: WorkspaceInfo,
    ) -> dict[str, str]:
        """Calculate hashes for output files.

        Args:
            step: Step definition
            workspace: Workspace info

        Returns:
            Dict mapping output paths to content hashes
        """
        import hashlib

        outputs = {}

        for output_path in step.outputs:
            full_path = workspace.workspace_path / output_path

            if full_path.exists() and full_path.is_file():
                content = full_path.read_bytes()
                content_hash = hashlib.md5(content).hexdigest()[:8]
                outputs[output_path] = content_hash

        return outputs
