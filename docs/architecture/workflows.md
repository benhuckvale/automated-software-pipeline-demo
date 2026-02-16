# Workflows

How workflows are defined, parsed, and executed.

## Workflow YAML Format

Workflows are defined in YAML files:

```yaml
workflow:
  name: solve-simple
  description: "3-step TDD workflow"

  steps:
    - id: clarify
      model: haiku
      wrapper: claude_code
      prompt_strategy: prompts/clarify_problem.md
      outputs:
        - context/clarified_problem.md
      timeout: 180
      max_turns: 10

    - id: write_tests
      model: sonnet
      wrapper: claude_code
      prompt_strategy: prompts/write_tests.md
      outputs:
        - project/solution.py
      depends_on:
        - clarify
      timeout: 240
      max_turns: 10

    - id: build_solution
      model: sonnet
      wrapper: claude_code
      prompt_strategy: prompts/build_tdd.md
      outputs:
        - project/solution.py
      depends_on:
        - write_tests
      timeout: 300
      max_turns: 15
```

## Step Configuration

Each step has:

- **id**: Unique identifier (used for dependencies)
- **model**: `haiku`, `sonnet`, or `opus`
- **wrapper**: Agent type (`claude_code` or `mock`)
- **prompt_strategy**: Path to prompt template file
- **outputs**: Expected output files (workspace-relative)
- **depends_on**: List of prerequisite step IDs
- **timeout**: Max execution time in seconds
- **max_turns**: Max agent conversation turns

## Dependency Resolution

The executor uses topological sort to determine execution order:

```python
# Workflow definition
clarify → write_tests → build_solution

# Execution order
1. clarify (no dependencies)
2. write_tests (waits for clarify)
3. build_solution (waits for write_tests)
```

**Circular dependencies are detected and rejected:**

```yaml
# ❌ Invalid - circular dependency
steps:
  - id: step1
    depends_on: [step2]
  - id: step2
    depends_on: [step1]
```

## Prompt Templates

Prompts support variable substitution:

```markdown
# Step 1: Clarify Problem

Read the problem from:
{workspace}/context/problem.txt

Write analysis to:
{workspace}/context/clarified_problem.md

Problem name: {problem_name}
```

**Available variables:**
- `{workspace}`: Absolute path to workspace
- `{problem_name}`: Problem name (from filename)
- Custom context variables passed to executor

## Built-in Workflows

### test-mock.yaml

Fast testing workflow using mock executor:

- **Purpose**: CI/CD testing, development
- **Speed**: < 1 second
- **Cost**: Free (no API calls)
- **Use**: `workflows/test-mock.yaml`

### solve-simple.yaml

Production workflow using Claude Code:

- **Purpose**: Real problem solving
- **Speed**: ~2 minutes
- **Cost**: API usage (varies by problem)
- **Use**: `workflows/solve-simple.yaml`

## Creating Custom Workflows

1. **Copy existing workflow**:
   ```bash
   cp workflows/solve-simple.yaml workflows/my-workflow.yaml
   ```

2. **Modify steps**:
   - Add/remove steps
   - Change models (haiku → sonnet for quality)
   - Adjust timeouts
   - Customize dependencies

3. **Create custom prompts**:
   ```bash
   cp prompts/clarify_problem.md prompts/my_prompt.md
   # Edit as needed
   ```

4. **Run your workflow**:
   ```bash
   pipeline run --workflow workflows/my-workflow.yaml --problem examples/reverse_string/problem.txt
   ```

## Advanced Patterns

### Parallel Steps

Steps with no dependencies can run in parallel (future enhancement):

```yaml
steps:
  - id: analyze_approach1
    # no dependencies

  - id: analyze_approach2
    # no dependencies

  - id: compare
    depends_on: [analyze_approach1, analyze_approach2]
```

### Multi-Implementation

Generate multiple solution approaches:

```yaml
steps:
  - id: clarify
    # ...

  - id: write_tests
    depends_on: [clarify]
    # ...

  - id: impl_hashmap
    depends_on: [write_tests]
    prompt_strategy: prompts/implement_hashmap.md

  - id: impl_iteration
    depends_on: [write_tests]
    prompt_strategy: prompts/implement_iteration.md
```

## Next Steps

- [Creating Problems](../guide/creating-problems.md) - Define your own problems
- [Running Workflows](../guide/running-workflows.md) - Execute and monitor
