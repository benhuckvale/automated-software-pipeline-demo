# Automated Software Pipeline

Small-scale demo of a fully automated AI-driven software delivery pipeline.

## Overview

The Automated Software Pipeline orchestrates Claude Code agents through a structured workflow to solve algorithmic coding problems automatically. It's designed as a toy project showcasing AI orchestration principles while being simple enough for educational purposes.

## What It Does

The pipeline takes a coding problem (like a leetcode challenge) and automatically:

1. **Clarifies** the problem by analyzing requirements and edge cases
2. **Writes Tests** following TDD with a reusable test mixin pattern
3. **Builds Solution** implementing code that passes all tests

**Input**: A problem description (e.g., "reverse a string")
**Output**: Working Python solution with comprehensive tests

## Key Features

- ✅ **Fully Automated**: End-to-end solution generation
- 🧪 **Test-Driven**: Generates tests before implementation
- 🔄 **Resumable**: Workflows can be interrupted and resumed
- 📊 **State Tracking**: Persistent state management
- 🎯 **Implementation Agnostic**: Test mixin pattern supports multiple approaches
- 🚀 **Fast Testing**: Mock executor for testing without API costs

## Quick Example

```bash
# Run a workflow
pdm run pipeline run \
  --workflow workflows/solve-simple.yaml \
  --problem examples/reverse_string/problem.txt

# Check status
pdm run pipeline status --workspace 00001

# Resume if interrupted
pdm run pipeline resume --workspace 00001
```

## Use Cases

- **Learning AI Orchestration**: Study how to coordinate multiple AI agents
- **TDD Practice**: Generate test suites automatically
- **Algorithm Study**: Compare different solution approaches
- **Educational Tool**: Demonstrate automated software pipelines

## Limitations

This is a **toy project** with intentional scope limitations:

- ❌ No external dependencies (single-file solutions only)
- ❌ Simple algorithmic problems only (no complex applications)
- ❌ No production deployment (educational/demo purposes)
- ⚠️ Requires Claude Code CLI for production workflows

## Next Steps

- [Installation](getting-started/installation.md) - Set up the pipeline
- [Quick Start](getting-started/quick-start.md) - Run your first workflow
- [Architecture](architecture/overview.md) - Understand how it works
