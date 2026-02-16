"""
Automated Software Pipeline - AI-driven workflow orchestration
"""
import structlog

__version__ = "0.1.0"

def configure_logging(workspace_log_path: str | None = None):
    """Configure structured logging for the pipeline.

    Args:
        workspace_log_path: Optional path to workspace-specific log file
    """
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]

    if workspace_log_path:
        # JSON logs to file
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Human-readable to console
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Configure console logging by default
configure_logging()
