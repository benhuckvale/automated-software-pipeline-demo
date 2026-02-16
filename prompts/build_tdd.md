# Step 3: Build Solution (TDD)

You are implementing a solution to make the tests pass.

## Input

Read the tests from:
```
{workspace}/project/solution.py
```

The file contains:
- A test mixin class with implementation-agnostic tests
- One or more implementation stubs (functions that raise `NotImplementedError`)
- Concrete test classes that link the mixin to specific implementations

## Your Task

Implement the solution function(s) to make all tests pass. Follow TDD approach:

1. **Identify the function(s)**: Find which function(s) raise `NotImplementedError`
2. **Understand the contract**: Read the test mixin to understand expected behavior (inputs → outputs)
3. **Implement the algorithm**: Write the solution using the approach indicated in the function name
4. **Run Tests**: Execute the tests to verify
5. **Iterate**: Fix any failures until all tests pass

## Requirements

**Keep unchanged:**
- Test mixin class and all test methods
- Concrete test classes
- Function signatures (names, parameters, return types)

**Implement:**
- The function body to replace `raise NotImplementedError(...)`
- Use the algorithm/approach indicated in the function name:
  - `using_slicing` → use Python slice notation
  - `using_hashmap` → use a dict/hash table
  - `using_iteration` → use a loop
  - `using_two_pointer` → use two-pointer technique
  - `using_recursion` → use recursive approach
  - etc.

**Code Quality:**
- Clean, readable, well-commented code
- Efficient implementation appropriate for the approach
- Handle all edge cases covered in tests
- Follow Python best practices

## Verification

Run the tests to ensure they all pass:
```bash
cd {workspace}/project
python solution.py --test
```

Or using unittest directly:
```bash
cd {workspace}/project
python -m unittest solution.py -v
```

**All tests MUST pass** before this step is complete.

## Output

The modified file should be written back to:
```
{workspace}/project/solution.py
```

With the solution function(s) fully implemented and all tests passing.

## Example

**Before (stub):**
```python
def reverse_string_using_slicing(s):
    """Reverse a string using Python slicing."""
    raise NotImplementedError("To be implemented in next step")
```

**After (implemented):**
```python
def reverse_string_using_slicing(s):
    """Reverse a string using Python slicing.

    Args:
        s: Input string
    Returns:
        Reversed string
    """
    return s[::-1]
```

## Notes

- If multiple implementations are present, implement ALL of them
- Each implementation may use a different algorithm (that's the point!)
- Tests are implementation-agnostic - they don't care HOW you solve it, only that you produce correct results
- Focus on correctness first, then optimize if needed
