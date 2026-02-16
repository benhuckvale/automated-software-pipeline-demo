# Running Workflows

Comprehensive guide to executing and managing workflows.

## Basic Usage

Run a workflow with a problem:

```bash
pdm run pipeline run \
  --workflow workflows/solve-simple.yaml \
  --problem examples/reverse_string/problem.txt
```

## Command Options

### run

Start a new workflow execution:

```bash
pipeline run --workflow WORKFLOW_FILE --problem PROBLEM_FILE
```

**Arguments:**
- `--workflow`: Path to workflow YAML file (required)
- `--problem`: Path to problem description file (optional)

**Example:**
```bash
pdm run pipeline run \
  --workflow workflows/test-mock.yaml \
  --problem examples/two_sum/problem.txt
```

### resume

Continue an interrupted workflow:

```bash
pipeline resume --workspace WORKSPACE_ID
```

**Arguments:**
- `--workspace`: Workspace ID to resume (required)

**Example:**
```bash
pdm run pipeline resume --workspace 00003
```

**When to use:**
- Workflow was interrupted (Ctrl+C)
- Step failed and you want to retry
- Execution timed out

### status

Show detailed workflow state:

```bash
pipeline status --workspace WORKSPACE_ID
```

**Example:**
```bash
pdm run pipeline status --workspace 00001
```

**Output:**
```
============================================================
Workspace: 00001
Workflow: solve-simple
Status: completed
============================================================

Current step: None

Completed steps: 3
  ✓ clarify (250 tokens)
  ✓ write_tests (300 tokens)
  ✓ build_solution (400 tokens)

Total tokens: 950
Duration: 108.5s
============================================================
```

### list

List all workspaces:

```bash
pipeline list
```

**Example output:**
```
============================================================
Workspaces (3):
============================================================

00003: solve-simple - ✓ complete
00002: test-mock - ✓ complete
00001: solve-simple - ⏳ in progress
```

## Workflow Selection

### Mock Workflow (Fast)

Best for testing and development:

```bash
pdm run pipeline run \
  --workflow workflows/test-mock.yaml \
  --problem examples/reverse_string/problem.txt
```

**Characteristics:**
- ⚡ Fast: < 1 second
- 💰 Free: No API costs
- 🎯 Purpose: Testing, CI/CD

### Production Workflow

Uses real Claude Code inference:

```bash
pdm run pipeline run \
  --workflow workflows/solve-simple.yaml \
  --problem examples/two_sum/problem.txt
```

**Characteristics:**
- ⏱️ Slower: ~2 minutes
- 💸 Costs: API usage
- 🎯 Purpose: Real problem solving
- 📋 Requires: Claude Code CLI installed

## Monitoring Execution

### Real-time Output

The CLI shows progress as steps execute:

```
✓ Loaded workflow: solve-simple
  Steps: 3
✓ Created workspace: 00004
  Path: workspaces/00004

🚀 Starting workflow execution...

[step logs appear here]
```

### Logs

Detailed logs are saved to workspace:

```bash
# View pipeline logs
cat workspaces/00001/logs/pipeline.log

# Follow live (during execution)
tail -f workspaces/00001/logs/pipeline.log
```

### State File

Raw state is in JSON:

```bash
# View full state
cat workspaces/00001/state/workflow_state.json | python -m json.tool
```

## Handling Failures

### Step Fails

If a step fails:

1. **Check status**:
   ```bash
   pipeline status --workspace 00001
   ```

2. **Inspect error**:
   ```json
   {
     "step_id": "clarify",
     "status": "failed",
     "error": "Expected outputs not created: ['context/clarified_problem.md']"
   }
   ```

3. **Resume to retry**:
   ```bash
   pipeline resume --workspace 00001
   ```

### Workflow Interrupted

If you press Ctrl+C:

```
⚠️  Workflow interrupted by user
   Resume with: pipeline resume --workspace 00001
```

Just run the resume command.

### Timeout

If a step times out:

1. Check the timeout setting in workflow YAML
2. Increase if needed:
   ```yaml
   - id: clarify
     timeout: 300  # increase from 180
   ```
3. Resume the workflow

## Workspace Management

### Inspect Workspace

After execution, explore the workspace:

```bash
# List all files
ls -R workspaces/00001/

# View solution
cat workspaces/00001/project/solution.py

# View clarification
cat workspaces/00001/context/clarified_problem.md

# View problem
cat workspaces/00001/context/problem.txt
```

### Clean Up

Workspaces are kept by default. To clean up:

```bash
# Remove specific workspace
rm -rf workspaces/00001

# Remove all workspaces
rm -rf workspaces/
```

## Next Steps

- [Understanding Output](understanding-output.md) - Interpret generated code
- [Creating Problems](creating-problems.md) - Add your own problems
