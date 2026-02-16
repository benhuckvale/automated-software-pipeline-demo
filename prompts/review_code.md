# Step 4: Code Review

You are reviewing a Python solution for quality, correctness, and optimization opportunities.

## Input

Read the solution from:
```
{workspace}/project/solution.py
```

The file contains:
- Test mixin class with comprehensive test cases
- One or more solution implementations
- Concrete test classes verifying the implementations

Also reference the original problem clarification:
```
{workspace}/context/clarified_problem.md
```

## Your Task

Conduct a thorough code review analyzing:

### 1. Correctness
- ✅ Do all tests pass?
- ✅ Are all edge cases from the problem handled?
- ❌ Any missing test coverage?
- ❌ Any logical errors in the implementation?

### 2. Algorithm & Complexity
- What is the time complexity? O(?)
- What is the space complexity? O(?)
- Is this optimal for the problem?
- **Are there better algorithms available?** (e.g., O(n³) → O(n²), O(n²) → O(n))
- Can we reduce space usage?

### 3. Code Quality
- **Readability**: Are variable names clear and descriptive?
- **Structure**: Is the code well-organized and easy to follow?
- **Duplication**: Any repeated code that could be extracted?
- **Pythonic**: Does it follow Python best practices and idioms?

### 4. Edge Cases & Robustness
- Are input validations needed?
- How does it handle empty inputs?
- How does it handle single-element inputs?
- Are there any potential runtime errors?

### 5. Documentation
- Are docstrings present and accurate?
- Do they explain the algorithm approach?
- Is complexity documented?

## Review Format

Structure your review as follows:

```markdown
# Code Review

## Summary
[One-paragraph overview of the solution quality]

## What Works Well
- [List positive aspects]

## Issues Found

### Critical (Must Fix)
- [Issues that affect correctness or cause errors]

### Optimization Opportunities
- [Algorithm improvements that would reduce complexity]
- [Specific suggestions: "Consider using X instead of Y"]

### Code Quality Improvements
- [Readability, naming, structure improvements]
- [Non-critical but would improve maintainability]

## Recommended Changes
1. [Specific, actionable change]
2. [Specific, actionable change]
3. [...]

## Complexity Analysis
- Current time complexity: O(?)
- Current space complexity: O(?)
- Optimal achievable: O(?) time, O(?) space
- [Explain if current solution is optimal or can be improved]
```

## Output

Write your review to:
```
{workspace}/context/review_notes.md
```

Be specific and actionable. Focus on the most impactful improvements first.

## Notes

- Be constructive - acknowledge what works well
- Prioritize correctness > performance > code quality
- Suggest specific improvements, not just "make it better"
- Reference actual lines/patterns from the code
- If the code is already excellent, say so! (Not all code needs refinement)
