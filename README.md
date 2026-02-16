# Automated Software Pipeline Demo

Small-scale demo of an fully automated AI-driven software delivery pipeline.

Uses AI agents to analyse, build, test and review code in steps completely
automatically. But scope is such that it's only for solving very small and
tightly scoped algorithmic problems with no dependencies, such as leetcode.com
problems. Intention is this is a toy project showcasing principles and
techniques, whilst being simple enough to have an insignificant cost (in terms
of model usage) for demo and educational purposes.

## What It Does

Orchestrates Claude Code agents through multi-step workflows:

**Phase 1 (MVP) - 3 steps:**
1. **Clarify** - Analyze problem → write specification
2. **Write Tests** - Generate test suite (TDD)
3. **Build Solution** - Implement code to pass tests

**Phase 2 - 5 steps (with code review):**
1. **Clarify** - Analyze problem → write specification
2. **Write Tests** - Generate test suite (TDD)
3. **Build Solution** - Implement code to pass tests
4. **Review** - Identify quality issues and optimizations ⭐
5. **Refine** - Apply feedback, optimize algorithm ⭐

**Input**: A problem description (e.g., "reverse a string", "three sum")
**Output**: Working, reviewed, and optimized Python solution with tests

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

**Option 1: Mock workflow - Phase 1 (fast, no API calls)**
```bash
pdm run pipeline run --workflow workflows/test-mock.yaml --problem examples/reverse_string/problem.txt
```

**Option 2: Mock workflow - Phase 2 with review (fast, no API calls)**
```bash
pdm run pipeline run --workflow workflows/test-review-mock.yaml --problem examples/three_sum/problem.txt
```

**Option 3: Production workflow - Phase 1 (requires Claude Code CLI)**
```bash
# Run from outside Claude Code session
pdm run pipeline run --workflow workflows/solve-simple.yaml --problem examples/reverse_string/problem.txt
```

**Option 4: Production workflow - Phase 2 with review (requires Claude Code CLI)**
```bash
# Run from outside Claude Code session
pdm run pipeline run --workflow workflows/solve-with-review.yaml --problem examples/three_sum/problem.txt
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
- **docs/** - Comprehensive MkDocs documentation site

## Requirements

- Python 3.11+
- pdm
- Claude Code CLI (for production workflows)
