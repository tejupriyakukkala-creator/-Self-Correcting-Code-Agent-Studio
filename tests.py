"""
Test suite definitions for the self-correcting agent.
Contains core tasks, complex algorithmic/data structure tasks, as well as controlled self-correction and timeout demonstrations.
"""

TASKS = [
    {
        "id": 1,
        "name": "Reverse String",
        "task": """Write a function reverse(s) that returns the reversed string.

Required tests:
assert reverse("abc") == "cba"
assert reverse("hello") == "olleh"
assert reverse("") == ""
print("All reverse string tests passed!")"""
    },
    {
        "id": 2,
        "name": "Palindrome",
        "task": """Write a function is_palindrome(s) that returns True when the string is a palindrome and False otherwise.

Required tests:
assert is_palindrome("madam") is True
assert is_palindrome("racecar") is True
assert is_palindrome("hello") is False
print("All palindrome tests passed!")"""
    },
    {
        "id": 3,
        "name": "Factorial",
        "task": """Write a function factorial(n) that returns the factorial of n.

Required tests:
assert factorial(0) == 1
assert factorial(1) == 1
assert factorial(5) == 120
assert factorial(7) == 5040
print("All factorial tests passed!")"""
    },
    {
        "id": 4,
        "name": "Prime Number",
        "task": """Write a function is_prime(n) that returns True if n is prime and False otherwise.

Required tests:
assert is_prime(2) is True
assert is_prime(3) is True
assert is_prime(4) is False
assert is_prime(17) is True
assert is_prime(1) is False
print("All prime tests passed!")"""
    },
    {
        "id": 5,
        "name": "Fibonacci",
        "task": """Write a function fibonacci(n) that returns the nth Fibonacci number, where fibonacci(0) == 0 and fibonacci(1) == 1.

Required tests:
assert fibonacci(0) == 0
assert fibonacci(1) == 1
assert fibonacci(5) == 5
assert fibonacci(10) == 55
print("All fibonacci tests passed!")"""
    },
    {
        "id": 16,
        "name": "Sum of Array",
        "task": """Write a function sum_array(arr) that returns the sum of elements in a list.

Required tests:
assert sum_array([1, 2, 3, 4, 5]) == 15
assert sum_array([10, -2, 3]) == 11
assert sum_array([]) == 0
print("All sum of array tests passed!")"""
    },
    {
        "id": 6,
        "name": "Binary Search",
        "task": """Write a function binary_search(arr, target) that returns the index of target in sorted array arr, or -1 if target is not found.

Required tests:
assert binary_search([1, 2, 3, 4, 5, 6], 4) == 3
assert binary_search([1, 3, 5, 7], 1) == 0
assert binary_search([1, 3, 5, 7], 8) == -1
print("All binary search tests passed!")"""
    },
    {
        "id": 7,
        "name": "Frequency Counter",
        "task": """Write a function count_frequency(items) that returns a dictionary mapping each item to its count.

Required tests:
assert count_frequency(["a", "b", "a", "c", "b", "a"]) == {"a": 3, "b": 2, "c": 1}
assert count_frequency([1, 1, 1]) == {1: 3}
assert count_frequency([]) == {}
print("All frequency counter tests passed!")"""
    },
    {
        "id": 8,
        "name": "Two Sum",
        "task": """Write a function two_sum(nums, target) that returns indices of the two numbers such that they add up to target.

Required tests:
assert two_sum([2, 7, 11, 15], 9) == [0, 1]
assert two_sum([3, 2, 4], 6) == [1, 2]
print("All two sum tests passed!")"""
    },
    {
        "id": 9,
        "name": "Valid Parentheses",
        "task": """Write a function is_valid_parentheses(s) that determines if input string containing brackets '()[]{}' is valid.

Required tests:
assert is_valid_parentheses("()") is True
assert is_valid_parentheses("()[]{}") is True
assert is_valid_parentheses("(]") is False
assert is_valid_parentheses("([)]") is False
print("All valid parentheses tests passed!")"""
    },
    {
        "id": 10,
        "name": "Flatten Nested List",
        "task": """Write a function flatten_list(nested_list) that flattens a arbitrarily nested list into a single list.

Required tests:
assert flatten_list([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]
assert flatten_list([]) == []
print("All flatten list tests passed!")"""
    },
    {
        "id": 11,
        "name": "Count Vowels",
        "task": """Write a function count_vowels(s) that returns the number of vowels in a string s.

Required tests:
assert count_vowels("hello") == 2
assert count_vowels("sky") == 0
assert count_vowels("AEIOU") == 5
print("All vowel count tests passed!")"""
    },
    {
        "id": 12,
        "name": "Leap Year Checker",
        "task": """Write a function is_leap_year(year) that returns True if year is a leap year and False otherwise.

Required tests:
assert is_leap_year(2020) is True
assert is_leap_year(2021) is False
assert is_leap_year(2000) is True
assert is_leap_year(1900) is False
print("All leap year tests passed!")"""
    },
    {
        "id": 13,
        "name": "Find Missing Number",
        "task": """Write a function find_missing_number(nums) that finds the missing number from an array containing n distinct numbers from 0 to n.

Required tests:
assert find_missing_number([3, 0, 1]) == 2
assert find_missing_number([0, 1]) == 2
assert find_missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1]) == 8
print("All missing number tests passed!")"""
    },
    {
        "id": 14,
        "name": "Celsius to Fahrenheit",
        "task": """Write a function celsius_to_fahrenheit(c) that converts Celsius temperature to Fahrenheit.

Required tests:
assert celsius_to_fahrenheit(0) == 32
assert celsius_to_fahrenheit(100) == 212
assert celsius_to_fahrenheit(37) == 98.6
print("All temperature conversion tests passed!")"""
    },
    {
        "id": 15,
        "name": "Matrix Transpose",
        "task": """Write a function matrix_transpose(matrix) that transposes a 2D matrix.

Required tests:
assert matrix_transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]
assert matrix_transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
print("All matrix transpose tests passed!")"""
    }
]

# Controlled Demonstration Tasks

DEMO_SELF_CORRECT_TASK = {
    "name": "Factorial (Forced Failure & Self-Correction Demo)",
    "task": """Write a function factorial(n) that returns the factorial of n.

Required tests:
assert factorial(0) == 1
assert factorial(1) == 1
assert factorial(5) == 120
assert factorial(7) == 5040
print("All factorial tests passed!")""",
    "mock_responses": [
        # Attempt 1: Intentional bug (factorial(5) returns 100 instead of 120)
        '''def factorial(n):
    if n <= 1:
        return 1
    if n == 5:
        return 100  # Buggy implementation
    return n * factorial(n - 1)

assert factorial(0) == 1
assert factorial(1) == 1
assert factorial(5) == 120  # Will fail with AssertionError
assert factorial(7) == 5040
print("All tests passed!")''',

        # Attempt 2: Corrected implementation following feedback
        '''def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

assert factorial(0) == 1
assert factorial(1) == 1
assert factorial(5) == 120
assert factorial(7) == 5040
print("All tests passed!")'''
    ]
}

DEMO_TIMEOUT_TASK = {
    "name": "Infinite Loop Safety Demo",
    "task": """Write code that completes within timeout bounds.""",
    "mock_responses": [
        # Attempt 1: Infinite loop
        '''print("Starting long computation...")
import time

while True:
    time.sleep(0.1)
''',
        # Attempt 2: Corrected code without infinite loop
        '''print("Safe computation finished!")
assert True
'''
    ]
}

DEMO_SECURITY_TASK = {
    "name": "Security Guard Block Demo",
    "task": """Attempting prohibited system or file execution.""",
    "mock_responses": [
        # Attempt 1: Dangerous code trying os.system call
        '''import os
print("Attempting system command...")
os.system("echo Hacked")
''',
        # Attempt 2: Safe code after AST security check rejection
        '''print("Safe execution without system call!")
assert True
'''
    ]
}

