# Automated Software Pipeline Demo

Small-scale demo of an fully automated AI-driven software delivery pipeline.

Uses AI agents to analyse, build, test and review code in steps completely
automatically. But scope is such that it's only for solving very small and
tightly scoped algorithmic problems with no dependencies, such as leetcode.com
problems. Intention is this is a toy project showcasing principles and
techniques, whilst being simple enough to have an insignificant cost (in terms
of model usage) for demo and educational purposes.

## What It Does

Orchestrates Claude Code agents through a 3-step workflow:
1. **Clarify** - Analyze problem → write specification
2. **Write Tests** - Generate test suite (TDD)
3. **Build Solution** - Implement code to pass tests

**Input**: A problem description (e.g., "reverse a string")
**Output**: Working Python solution with tests

## Quick Start

### Setup

```bash
# Install dependencies
pdm install
```

### Run Tests

```bash
# Run all unit tests (33 tests)
pdm run pytest tests/ -v
```

### Run a Workflow

**Option 1: Mock workflow (fast, no API calls)**
```bash
pdm run pipeline run --workflow workflows/test-mock.yaml --problem examples/reverse_string/problem.txt
```

**Option 2: Production workflow (requires Claude Code CLI)**
```bash
pdm run pipeline run --workflow workflows/solve-simple.yaml --problem examples/reverse_string/problem.txt
```

### Other Commands

```bash
# List all workspaces
pdm run pipeline list

# Check workflow status
pdm run pipeline status --workspace 00001

# Resume interrupted workflow
pdm run pipeline resume --workspace 00001
```

## Project Structure

```
src/pipeline/       # Core implementation
tests/              # Unit tests
workflows/          # Workflow definitions (.yaml)
prompts/            # Prompt templates (.md)
examples/           # Sample problems
workspaces/         # Runtime artifacts (gitignored)
```

## Documentation

- **plan.md** - Original design document

## Requirements

- Python 3.11+
- pdm
- Claude Code CLI (for production workflows)
