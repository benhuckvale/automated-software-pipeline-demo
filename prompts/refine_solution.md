# Step 5: Refine Solution

You are improving a working solution based on code review feedback.

## Input

Read the current solution:
```
{workspace}/project/solution.py
```

Read the review feedback:
```
{workspace}/context/review_notes.md
```

Also reference:
```
{workspace}/context/clarified_problem.md
```

## Your Task

Apply the code review feedback to improve the solution. The tests already pass, so your goal is to:

### 1. Address Critical Issues
- Fix any correctness problems identified in review
- Handle edge cases that were missed
- Fix any bugs or logical errors

### 2. Optimize Algorithm (if suggested)
- Implement better algorithm if review identified optimization opportunity
- Example: Replace O(n³) nested loops with O(n²) two-pointer approach
- Example: Replace O(n) space with O(1) in-place algorithm
- **Maintain test compatibility** - tests should still pass with optimized version

### 3. Improve Code Quality
- Use clearer variable names
- Simplify complex logic
- Remove code duplication
- Add helpful comments for non-obvious logic
- Follow Python idioms and best practices

### 4. Enhance Documentation
- Add/improve docstrings
- Document algorithm approach
- Document time/space complexity
- Add inline comments where logic is subtle

## Requirements

**MUST preserve:**
- All existing tests (don't modify test classes)
- Test mixin structure
- Function signatures and naming conventions
- All tests MUST still pass after refinement

**CAN change:**
- Implementation details inside functions
- Algorithm approach (if it improves complexity)
- Variable names and code structure
- Comments and documentation
- Helper functions (add if they improve clarity)

**MUST improve:**
- Apply at least the high-priority items from review notes
- If algorithm optimization is suggested, implement it
- Ensure code is more readable than before

## Verification

After making changes, run tests to ensure nothing broke:
```bash
cd {workspace}/project
python solution.py --test
```

All tests MUST pass. If tests fail after your changes, fix the implementation.

## Output

Write the refined solution back to:
```
{workspace}/project/solution.py
```

## Example Transformation

**Before (naive, from review: "Uses O(n³) nested loops - optimize to O(n²)"):**
```python
def three_sum_using_brute_force(nums):
    """Find all triplets that sum to zero."""
    result = []
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    triplet = sorted([nums[i], nums[j], nums[k]])
                    if triplet not in result:
                        result.append(triplet)
    return result
```

**After (optimized to O(n²) using two-pointer):**
```python
def three_sum_using_two_pointer(nums):
    """Find all triplets that sum to zero using two-pointer technique.

    Algorithm:
    1. Sort the array O(n log n)
    2. For each element, use two pointers to find pairs that complete triplet
    3. Skip duplicates to avoid duplicate triplets

    Time complexity: O(n²)
    Space complexity: O(1) excluding output

    Args:
        nums: List of integers

    Returns:
        List of unique triplets [a, b, c] where a + b + c = 0
    """
    nums.sort()
    result = []
    n = len(nums)

    for i in range(n - 2):
        # Skip duplicate values for first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        left, right = i + 1, n - 1

        while left < right:
            total = nums[i] + nums[left] + nums[right]

            if total == 0:
                result.append([nums[i], nums[left], nums[right]])

                # Skip duplicates for second and third elements
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1

                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result
```

## Notes

- This is about improvement, not complete rewrite
- Keep changes focused on review feedback
- Balance perfectionism with pragmatism - significant improvements are good, but don't spend hours on tiny tweaks
- If review says "already excellent", minimal changes are fine
- Always verify tests pass after refinement
