# Quick Start

Get up and running with your first workflow in under 2 minutes.

## Run a Mock Workflow

The fastest way to see the pipeline in action (no API costs):

```bash
pdm run pipeline run \
  --workflow workflows/test-mock.yaml \
  --problem examples/reverse_string/problem.txt
```

This runs a complete 3-step workflow using the mock executor:

1. **Clarify** - Analyzes the problem (< 1s)
2. **Write Tests** - Generates test suite (< 1s)
3. **Build Solution** - Implements solution (< 1s)

Expected output:

```
✓ Loaded workflow: test-mock
  Steps: 3
✓ Created workspace: 00001
  Path: workspaces/00001

🚀 Starting workflow execution...

============================================================
✓ Workflow completed successfully

Workspace: 00001
Steps completed: 3/3
Total tokens: 750
Duration: 0.0s

Step Status:
  ✓ clarify: completed
  ✓ write_tests: completed
  ✓ build_solution: completed
============================================================
```

## Inspect Results

Check the generated files:

```bash
# View the solution
cat workspaces/00001/project/solution.py

# View the clarification
cat workspaces/00001/context/clarified_problem.md
```

## List Workspaces

```bash
pdm run pipeline list
```

## Check Status

```bash
pdm run pipeline status --workspace 00001
```

## Run with Claude Code (Optional)

If you have Claude Code CLI installed:

```bash
pdm run pipeline run \
  --workflow workflows/solve-simple.yaml \
  --problem examples/reverse_string/problem.txt
```

This uses real AI inference and takes ~2 minutes.

## Try Another Problem

```bash
pdm run pipeline run \
  --workflow workflows/test-mock.yaml \
  --problem examples/two_sum/problem.txt
```

## Resume a Workflow

If a workflow is interrupted (Ctrl+C):

```bash
pdm run pipeline resume --workspace 00001
```

## Next Steps

- [Creating Problems](../guide/creating-problems.md) - Add your own problems
- [Running Workflows](../guide/running-workflows.md) - Advanced usage
- [Architecture](../architecture/overview.md) - How it works
