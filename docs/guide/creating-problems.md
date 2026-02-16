# Creating Problems

How to add your own coding problems to the pipeline.

## Problem File Format

Problems are simple text files with markdown formatting:

```markdown
# Problem Title

Brief description of what needs to be solved.

## Input
- Description of input parameters
- Types and constraints

## Output
- Description of expected output
- Format and types

## Examples

Example 1:
Input: example input
Output: expected output

Example 2:
Input: another input
Output: another output

## Constraints
- Performance requirements
- Edge cases to consider
- Any limitations
```

## Example: Reverse String

```markdown
# Reverse String

Write a function that reverses a string.

## Input
- A string `s` (0 ≤ length ≤ 10,000)

## Output
- The string reversed

## Examples

Example 1:
Input: s = "hello"
Output: "olleh"

Example 2:
Input: s = ""
Output: ""

## Constraints
- The input contains only ASCII characters
- O(n) time complexity preferred
```

## Directory Structure

Organize problems by directory:

```
examples/
  reverse_string/
    problem.txt
  two_sum/
    problem.txt
  fibonacci/
    problem.txt
```

## Problem Guidelines

### Good Problems

✅ **Clear and specific**
```markdown
# Find Maximum

Given an array of integers, return the maximum value.
```

✅ **Include examples**
```markdown
Example 1:
Input: [1, 5, 3]
Output: 5
```

✅ **Specify constraints**
```markdown
- Array length: 1 ≤ n ≤ 10,000
- Values: -10^9 ≤ val ≤ 10^9
```

✅ **Self-contained**
- No external dependencies
- Single-file solution
- Standard library only

### Problems to Avoid

❌ **Too vague**
```markdown
# Do something with numbers
Process some data.
```

❌ **Requires external dependencies**
```markdown
# Web Scraper
Use BeautifulSoup to scrape websites...
```

❌ **Too complex**
```markdown
# Build a database engine
Implement a full SQL database with transactions...
```

## Testing Your Problem

1. **Create the problem file**:
   ```bash
   mkdir examples/my_problem
   echo "# My Problem..." > examples/my_problem/problem.txt
   ```

2. **Run with mock executor** (fast, free):
   ```bash
   pdm run pipeline run \
     --workflow workflows/test-mock.yaml \
     --problem examples/my_problem/problem.txt
   ```

3. **Check generated files**:
   ```bash
   cat workspaces/00001/context/clarified_problem.md
   cat workspaces/00001/project/solution.py
   ```

4. **Run with Claude Code** (production):
   ```bash
   pdm run pipeline run \
     --workflow workflows/solve-simple.yaml \
     --problem examples/my_problem/problem.txt
   ```

## Problem Categories

### String Manipulation
- Reverse, palindrome, anagrams
- Pattern matching, substring search
- Character counting, transformation

### Arrays
- Search, sort, find max/min
- Two-pointer techniques
- Sliding window problems

### Mathematics
- Fibonacci, factorials, primes
- GCD, LCM, number theory
- Combinatorics

### Data Structures
- Stack, queue operations
- Linked list manipulation
- Tree/graph traversal (if simple)

## Next Steps

- [Running Workflows](running-workflows.md) - Execute your problem
- [Understanding Output](understanding-output.md) - Interpret results
