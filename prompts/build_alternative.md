# Build Alternative Solution Task

You are a software engineer implementing an alternative algorithmic approach to an existing solution. Your task is to add a new implementation using a different algorithm while maintaining the existing test mixin pattern.

## Context

You are working in a workspace with:
- **Current solution**: `{workspace}/project/solution.py` - contains tests and at least one implementation
- **Performance analysis**: `{workspace}/context/performance_analysis.md` - recommends an alternative approach

## Your Task

Add a new implementation function using the alternative approach recommended in the performance analysis.

### Implementation Requirements

1. **Follow the test mixin pattern**:
   - Tests are defined in a mixin class like `TestMixin<Verb><Problem>`
   - Each implementation is a standalone function: `<verb>_<problem>_using_<approach>()`
   - Each concrete test class inherits from the mixin and assigns the implementation

2. **Naming convention**:
   - If the existing function is `solve_problem_using_brute_force()`, add `solve_problem_using_optimized()`
   - Use descriptive names that indicate the approach: `using_hashmap`, `using_two_pointers`, `using_binary_search`, etc.

3. **Add a new test class**:
   - Create a new test class that tests the new implementation
   - Name it like: `TestSolveProblemUsingOptimized(TestMixinSolveProblem, unittest.TestCase)`
   - Set the static method to your new implementation

4. **Preserve existing code**:
   - Do NOT modify or remove the existing implementation
   - Do NOT modify the test mixin or existing test classes
   - Only ADD new code

### Example Structure

If the file currently has:
```python
class TestMixinSolve_problem:
    solve_problem = None
    def test_basic(self): ...

def solve_problem_using_brute_force(input): ...

class TestSolveProblemUsingBruteForce(TestMixinSolve_problem, unittest.TestCase):
    solve_problem = staticmethod(solve_problem_using_brute_force)
```

You should add:
```python
def solve_problem_using_optimized(input):
    """Alternative approach using [describe technique].

    Time complexity: O(...)
    Space complexity: O(...)
    """
    # implementation here
    pass

class TestSolveProblemUsingOptimized(TestMixinSolve_problem, unittest.TestCase):
    solve_problem = staticmethod(solve_problem_using_optimized)
```

## Important Guidelines

1. **Correctness first**: The new implementation must pass all existing tests
2. **Document complexity**: Add a docstring with time/space complexity
3. **Run tests**: After implementing, run `python {workspace}/project/solution.py --test` to verify
4. **Handle edge cases**: Ensure the implementation handles all test cases, not just the happy path
5. **Match the interface**: The function signature must match exactly what the tests expect

## Success Criteria

- New implementation function added with descriptive `using_<approach>` name
- New test class added that inherits from test mixin
- All tests pass (both old and new implementations)
- Implementation uses the algorithmic approach suggested in performance analysis
- Code follows the existing style and conventions
- Docstring documents the complexity

## Verification

After completing the implementation, run:
```bash
cd {workspace}/project && python solution.py --test
```

All tests should pass, including tests for both the original and new implementations.
