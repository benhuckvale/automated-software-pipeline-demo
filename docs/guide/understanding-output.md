# Understanding Output

How to interpret and use the generated code.

## Output Structure

Each workflow execution creates files in the workspace:

```
workspaces/00001/
  context/
    problem.txt              # Original problem
    clarified_problem.md     # Analysis from step 1
  project/
    solution.py              # Generated solution with tests
  state/
    workflow_state.json      # Execution state
  logs/
    pipeline.log             # Detailed logs
```

## Solution File Structure

The generated `solution.py` follows a standard pattern:

```python
"""Solution and tests for reverse_string"""
import unittest

# Test Mixin - Implementation agnostic
class TestMixinReverse_string:
    reverse_string = None

    def test_basic_string(self):
        result = self.reverse_string("hello")
        self.assertEqual(result, "olleh")

    # ... more tests ...

# Implementation
def reverse_string_using_slicing(s):
    """Reverse a string using Python slicing."""
    return s[::-1]

# Concrete Test Class
class TestReverseStringUsingSlicing(TestMixinReverse_string, unittest.TestCase):
    reverse_string = staticmethod(reverse_string_using_slicing)

# Test Runner
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        unittest.main(argv=[''], verbosity=2, exit=True)
```

## Running the Solution

### Run Tests

```bash
cd workspaces/00001/project
python solution.py --test
```

**Expected output:**
```
test_basic_string ... ok
test_empty_string ... ok
test_single_char ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.001s

OK
```

### Run Solution Directly

Some solutions support direct execution:

```bash
cd workspaces/00001/project
python solution.py "hello"
# Output: olleh
```

## Test Mixin Pattern

The generated code uses a reusable test pattern:

### Why It Matters

✅ **Tests are implementation-agnostic**
- Same tests validate any algorithm
- Easy to add alternative implementations

✅ **Clean separation**
- Tests define the contract
- Implementations compete fairly

✅ **Easy to extend**
```python
# Add a new implementation
def reverse_string_using_iteration(s):
    result = []
    for char in s:
        result.insert(0, char)
    return ''.join(result)

# Add a test class
class TestReverseStringUsingIteration(TestMixinReverse_string, unittest.TestCase):
    reverse_string = staticmethod(reverse_string_using_iteration)
```

## Clarification Document

The `clarified_problem.md` contains structured analysis:

```markdown
# Problem Summary
Reverse a string - take input characters and return them in opposite order.

# Inputs
- String s (0 ≤ length ≤ 10,000, ASCII characters)

# Outputs
- Reversed string (same type as input)

# Constraints
- O(n) time complexity preferred
- O(1) extra space if possible

# Examples
1. "hello" → "olleh"
2. "" → ""
3. "a" → "a"

# Key Insights
- Character at index i moves to index n-1-i
- Multiple valid approaches (slicing, two-pointer, iteration)

# Edge Cases
- Empty string
- Single character
- Palindromes
```

## Validating Solutions

### Check Correctness

Run the tests:

```bash
cd workspaces/00001/project
python solution.py --test
```

All tests should pass.

### Check Implementation

Review the code:

```bash
cat workspaces/00001/project/solution.py
```

**Look for:**
- ✅ Proper function signature
- ✅ Docstrings
- ✅ Edge case handling
- ✅ Clean, readable code

### Manual Testing

Test with your own inputs:

```python
# In Python REPL
from solution import reverse_string_using_slicing

print(reverse_string_using_slicing("test"))
# Output: tset

print(reverse_string_using_slicing(""))
# Output:
```

## Common Issues

### Tests Fail

If generated tests fail:

1. **Check the error**:
   ```
   AssertionError: 'olleh' != 'hello'
   ```

2. **Review implementation**:
   - Logic error
   - Edge case missed
   - Incorrect understanding of problem

3. **Fix and re-run**:
   - Edit `solution.py`
   - Run tests again

### Import Errors

If you get import errors:

```python
ModuleNotFoundError: No module named 'numpy'
```

**Solution**: Problems should use standard library only. Update problem constraints.

### Performance Issues

If solution is slow:

1. Check complexity requirements
2. Profile the code
3. Try alternative approach (add new implementation)

## Comparing Implementations

If you add multiple implementations:

```python
# Add benchmark method to test mixin
def test_benchmark(self):
    import time
    s = "a" * 10000

    start = time.time()
    for _ in range(100):
        self.reverse_string(s)
    elapsed = time.time() - start

    print(f"\n{self.reverse_string.__name__}: {elapsed:.4f}s")
```

Run tests to see performance comparison.

## Next Steps

- [Creating Problems](creating-problems.md) - Add more problems
- [Testing](../development/testing.md) - Write tests for the pipeline
