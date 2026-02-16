# Step 2: Write Tests (TDD)

You are writing tests for a coding problem following Test-Driven Development.

## Input

Read the problem clarification from:
```
{workspace}/context/clarified_problem.md
```

## Your Task

Create a Python file with comprehensive **implementation-agnostic** tests using the test mixin pattern. The file should include:

### 1. Test Mixin Class

Create a test mixin that defines the test suite WITHOUT specifying an implementation:

```python
class TestMixin<Verb><Problem>:
    """Test suite for <problem> - implementation agnostic."""
    <verb>_<problem> = None  # Will be set by concrete test classes

    def test_basic_case(self):
        # Test using self.<verb>_<problem>()
        pass

    def test_edge_case_empty(self):
        pass

    # ... more tests ...
```

**Naming Convention:**
- Choose the best verb: `solve_`, `find_`, `reverse_`, `calculate_`, etc.
- Example: `TestMixinReverse_string` with `reverse_string = None`
- Example: `TestMixinFind_motif` with `find_motif = None`
- Example: `TestMixinSolve_two_sum` with `solve_two_sum = None`

### 2. Implementation Stub

Create ONE initial implementation stub that will be completed in the next step:

```python
def <verb>_<problem>_using_<approach>(*args):
    """<Problem description> using <approach>.

    Args: (based on problem requirements)
    Returns: (based on problem requirements)
    """
    raise NotImplementedError("To be implemented in next step")
```

**Choosing the approach name:**
- Pick a reasonable default approach based on the problem
- Examples: `using_iteration`, `using_slicing`, `using_hashmap`, `using_two_pointer`, `using_recursion`
- The approach should be feasible for the problem (don't suggest `using_hashmap` if it doesn't make sense)

### 3. Concrete Test Class

Create one concrete test class that connects the mixin to the implementation:

```python
class Test<Verb><Problem>Using<Approach>(TestMixin<Verb><Problem>, unittest.TestCase):
    <verb>_<problem> = staticmethod(<verb>_<problem>_using_<approach>)
```

### 4. Test Runner

Add command-line support:

```python
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run tests
        unittest.main(argv=[''], verbosity=2, exit=True)
```

## Critical Requirements

**Tests MUST be implementation-agnostic:**
- ✅ Test the contract/behavior (inputs → outputs)
- ✅ Test edge cases (empty, single element, duplicates, etc.)
- ✅ Test correctness across different inputs
- ❌ DON'T test implementation details (e.g., "must use a hashmap", "must iterate exactly N times")
- ❌ DON'T make assumptions about the approach used

**Why:** The same test suite will be used to validate multiple implementations using different algorithms. Tests should only verify that the function produces correct results, not HOW it achieves them.

## Example Structure

```python
"""Solution and tests for {problem_name}"""
import unittest

class TestMixinSolve_reverse_string:
    """Test suite for string reversal - implementation agnostic."""
    reverse_string = None

    def test_basic_string(self):
        result = self.reverse_string("hello")
        self.assertEqual(result, "olleh")

    def test_empty_string(self):
        result = self.reverse_string("")
        self.assertEqual(result, "")

    def test_single_char(self):
        result = self.reverse_string("a")
        self.assertEqual(result, "a")

    # ... more tests ...


def reverse_string_using_slicing(s):
    """Reverse a string using Python slicing.

    Args:
        s: Input string
    Returns:
        Reversed string
    """
    raise NotImplementedError("To be implemented in next step")


class TestReverseStringUsingSlicing(TestMixinSolve_reverse_string, unittest.TestCase):
    reverse_string = staticmethod(reverse_string_using_slicing)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        unittest.main(argv=[''], verbosity=2, exit=True)
```

## Output

Write the test file to:
```
{workspace}/project/solution.py
```

The tests should FAIL when run (because implementation raises NotImplementedError) - this is correct TDD!
