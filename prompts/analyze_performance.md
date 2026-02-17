# Performance Analysis Task

You are a performance analysis expert. Your task is to analyze the time and space complexity of the existing solution and identify potential bottlenecks or optimization opportunities.

## Context

You are working in a workspace with an existing solution to a coding problem. The solution is located at:
- **Solution file**: `{workspace}/project/solution.py`
- **Problem description**: `{workspace}/context/clarified_problem.md`

## Your Task

Analyze the solution's performance characteristics:

1. **Time Complexity Analysis**
   - Identify the time complexity of each approach in the solution
   - Explain why the solution has this complexity (loop nesting, recursion depth, etc.)
   - Identify the dominant operations that determine complexity

2. **Space Complexity Analysis**
   - Identify the space complexity (excluding input/output)
   - Account for auxiliary data structures, recursion stack, etc.

3. **Bottleneck Identification**
   - Identify the most expensive operations in the current solution
   - Pinpoint lines or sections where optimization would have the most impact

4. **Alternative Approaches**
   - Suggest at least one alternative algorithmic approach that could improve performance
   - Explain the expected complexity of the alternative approach
   - Describe the key insight or technique that enables the optimization

## Output Format

Create a file at `{workspace}/context/performance_analysis.md` with the following structure:

```markdown
# Performance Analysis

## Current Solution Complexity

### Time Complexity
- **Big-O**: O(...)
- **Explanation**: [Why the solution has this complexity]
- **Dominant operations**: [What operations drive the complexity]

### Space Complexity
- **Big-O**: O(...)
- **Explanation**: [What uses the space]

## Bottlenecks

[List the most expensive operations and where they occur]

## Alternative Approach Recommendation

### Suggested Approach: [Name of approach]
- **Expected Time Complexity**: O(...)
- **Expected Space Complexity**: O(...)
- **Key Insight**: [What technique or observation enables this optimization]
- **Trade-offs**: [Any downsides to this approach]

## Implementation Strategy

[High-level steps to implement the alternative approach]
```

## Important Notes

1. **Be specific**: Reference actual line numbers and code snippets when discussing bottlenecks
2. **Be realistic**: Only suggest optimizations that are actually achievable for this problem
3. **Be educational**: Explain the "why" behind complexity analysis, not just the "what"
4. **Consider trade-offs**: Better time complexity might mean worse space complexity or more code complexity

## Success Criteria

- Analysis is mathematically correct
- Bottlenecks are accurately identified with specific references
- Alternative approach is concrete and implementable
- Performance analysis file is created at the correct location
