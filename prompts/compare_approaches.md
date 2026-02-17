# Compare Approaches Task

You are a technical advisor making evidence-based recommendations. Your task is to synthesize the performance analysis and benchmark results to recommend the best approach for this problem.

## Context

You are working in a workspace with:
- **Solution file**: `{workspace}/project/solution.py` - contains multiple implementations
- **Performance analysis**: `{workspace}/context/performance_analysis.md` - theoretical analysis
- **Benchmark results**: `{workspace}/context/benchmark_results.md` - empirical measurements
- **Problem description**: `{workspace}/context/clarified_problem.md` - problem requirements

## Your Task

Synthesize all available information to create a comprehensive comparison and recommendation.

### Analysis Requirements

1. **Verify theoretical predictions**:
   - Do the benchmark results match the predicted complexity?
   - If not, explain the discrepancy (hidden constants, small input effects, etc.)

2. **Consider multiple factors**:
   - **Performance**: Which is faster? At what scale does it matter?
   - **Code clarity**: Which is easier to understand and maintain?
   - **Space efficiency**: Which uses less memory?
   - **Implementation complexity**: Which is simpler to implement correctly?

3. **Context-aware recommendation**:
   - Consider the problem constraints (typical input sizes, frequency of use)
   - Balance theoretical complexity with practical considerations
   - Acknowledge when "premature optimization" might apply

### Output Format

Create `{workspace}/context/comparison_report.md`:

```markdown
# Approach Comparison and Recommendation

## Implementations Compared

### Approach 1: [Name]
- **Time Complexity**: O(...)
- **Space Complexity**: O(...)
- **Lines of Code**: [count]
- **Key Technique**: [brief description]

### Approach 2: [Name]
- **Time Complexity**: O(...)
- **Space Complexity**: O(...)
- **Lines of Code**: [count]
- **Key Technique**: [brief description]

## Performance Analysis

### Theoretical Complexity
[Summary of expected performance based on Big-O analysis]

### Empirical Results
[Summary of actual benchmark results]

### Verification
- ✅/❌ Benchmark results match theoretical predictions
- [Explanation of any discrepancies]

## Multi-Factor Comparison

| Factor | Approach 1 | Approach 2 | Winner |
|--------|------------|------------|--------|
| Time Complexity (theoretical) | O(...) | O(...) | [Which is better] |
| Actual Speed (n=1000) | [time] | [time] | [Which is faster] |
| Space Complexity | O(...) | O(...) | [Which uses less] |
| Code Clarity | [rating] | [rating] | [Which is clearer] |
| Lines of Code | [count] | [count] | [Which is shorter] |
| Implementation Difficulty | [rating] | [rating] | [Which is easier] |

## Recommendation

### For this problem: **[Recommended Approach]**

**Rationale**:
[Clear explanation of why this approach is recommended]

**When to use this approach**:
- [Scenario 1 where this approach excels]
- [Scenario 2 where this approach excels]

**When to consider the alternative**:
- [Scenario where the other approach might be better]

## Trade-offs Summary

**Choosing [Recommended Approach]**:
- ✅ Advantages: [list]
- ❌ Disadvantages: [list]

**Choosing [Alternative Approach]**:
- ✅ Advantages: [list]
- ❌ Disadvantages: [list]

## Scaling Considerations

[Discussion of how the choice affects performance at different scales]

Example scenarios:
- **Small inputs (n < 100)**: [Which approach and why]
- **Medium inputs (n = 1,000-10,000)**: [Which approach and why]
- **Large inputs (n > 100,000)**: [Which approach and why]

## Conclusion

[Final summary paragraph that contextualizes the recommendation based on the problem's actual requirements and typical use cases]
```

## Important Guidelines

1. **Be honest about trade-offs**: No approach is perfect for all scenarios
2. **Use evidence**: Reference specific numbers from benchmarks
3. **Be practical**: Consider real-world factors beyond just Big-O complexity
4. **Be decisive**: Make a clear recommendation, but acknowledge context matters
5. **Educate**: Explain the reasoning so the reader learns general principles

## Success Criteria

- Comparison report is comprehensive and well-structured
- Recommendation is clear and well-justified
- Analysis considers multiple factors (not just speed)
- Trade-offs are honestly presented
- Report references actual data from benchmarks and analysis
- Conclusion is actionable and context-aware

## Note on Objectivity

Your goal is not to advocate for the "optimal" solution, but to present an honest analysis of trade-offs. Sometimes the "slower" approach is the right choice due to simplicity or readability. Make your recommendation based on the full context of the problem.
