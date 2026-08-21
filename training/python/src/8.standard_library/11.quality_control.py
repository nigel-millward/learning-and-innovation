# =========================================
# 1. Quality Control (Testing)
# =========================================
"""
High-quality software is built by testing code regularly.

Testing helps to:
- Detect errors early
- Ensure code behaves as expected
- Prevent regressions when making changes

Python provides built-in tools for writing and running tests.
"""


# =========================================
# 1.1 Testing with doctest
# =========================================
"""
The doctest module allows you to embed tests directly in docstrings.

These tests:
- Serve as examples for users
- Are automatically verified
"""

def average(values):
    """Computes the arithmetic mean of a list of numbers.

    >>> print(average([20, 30, 70]))
    40.0
    """
    return sum(values) / len(values)


import doctest

doctest.testmod()  # Runs all doctests in the module


"""
If the output matches the expected result:
- No output is shown
- Errors are reported only when tests fail
"""


# =========================================
# 1.2 Why Use doctest?
# =========================================
"""
doctest is useful because:

- It keeps documentation and tests together
- It is simple to write and maintain
- It verifies examples automatically
"""


# =========================================
# 1.3 Testing with unittest
# =========================================
"""
The unittest module provides a more structured testing framework.

It is suitable for:
- Larger projects
- Complex test cases
- Automated testing environments
"""

import unittest

class TestStatisticalFunctions(unittest.TestCase):

    def test_average(self):
        self.assertEqual(average([20, 30, 70]), 40.0)
        self.assertEqual(round(average([1, 5, 7]), 1), 4.3)

        with self.assertRaises(ZeroDivisionError):
            average([])

        with self.assertRaises(TypeError):
            average(20, 30, 70)


# Run tests (typically from command line)
# python test_file.py
# Or:
# unittest.main()


# =========================================
# 1.4 Common Assertions
# =========================================
"""
unittest provides assertion methods:

- assertEqual(a, b)
- assertTrue(x)
- assertFalse(x)
- assertRaises(Exception)
"""

# Example:
# self.assertEqual(2 + 2, 4)


# =========================================
# 1.5 Running Tests
# =========================================
"""
Tests can be run:

- From the command line:
    python -m unittest

- Automatically during development
"""


# =========================================
# 1.6 doctest vs unittest
# =========================================
"""
doctest:
- Simple
- Great for examples
- Best for small functions

unittest:
- More powerful
- Supports larger test suites
- Better for production code
"""


# =========================================
# 1.7 Common Use Cases
# =========================================
"""
Testing is used for:

- Verifying function correctness
- Checking edge cases
- Preventing bugs during updates
"""


# =========================================
# 1.8 Key Idea
# =========================================
"""
Testing ensures code reliability.

It should be:
- Written alongside code
- Run frequently
- Used to confirm behaviour
"""


# =========================================
# 1.9 Summary
# =========================================
"""
Core tools:

- doctest → embed tests in documentation
- unittest → structured testing framework

Best practices:
- Write tests early and often
- Use doctest for simple examples
- Use unittest for larger systems

Core idea:
"Test your code to ensure correctness and reliability"
"""