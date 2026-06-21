# =========================================
# 1. Exceptions: The Basics
# =========================================
"""
An exception is an error that occurs during program execution.

Even if code is syntactically correct, it may still fail when it runs.

When an exception occurs:
- Python stops normal execution
- An error message is displayed (unless handled)
"""


# =========================================
# 1.1 Common Exceptions
# =========================================
"""
Examples of runtime errors (exceptions):
"""

# Division by zero
# 10 * (1 / 0)

# Name not defined
# 4 + spam * 3

# Type mismatch
# '2' + 2


"""
Typical output looks like:

ZeroDivisionError: division by zero
NameError: name 'spam' is not defined
TypeError: can only concatenate str (not "int") to str

The final line explains what went wrong.
"""


# =========================================
# 1.2 Exception Types
# =========================================
"""
Each exception has a type.

Common built-in exception types include:
- ZeroDivisionError
- NameError
- TypeError
- ValueError
- IndexError

These names are built-in identifiers (not keywords).
"""

try:
    1 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")

# Outputs: Cannot divide by zero


# =========================================
# 1.3 Traceback Information
# =========================================
"""
When an exception occurs, Python provides a traceback.

This shows:
- Where the error happened
- The call stack (sequence of function calls)
"""

def divide(a, b):
    return a / b

# divide(10, 0)


"""
Example traceback:

Traceback (most recent call last):
  File "example.py", line X, in <module>
    divide(10, 0)
  File "example.py", line Y, in divide
    return a / b
ZeroDivisionError: division by zero

Key parts:
- File and line numbers
- Code that caused the error
- Exception type and message
"""


# =========================================
# 1.4 Handling Exceptions (try/except)
# =========================================
"""
You can prevent crashes by handling exceptions.

Use:
- try → code that may fail
- except → what to do if it fails
"""

try:
    result = 10 / 0
except ZeroDivisionError:
    print("Error: division by zero")

# Outputs: Error: division by zero


# =========================================
# 1.5 Multiple Exception Handling
# =========================================
"""
You can handle different types of exceptions separately.
"""

try:
    value = int("abc")
except ValueError:
    print("Conversion failed")
except TypeError:
    print("Wrong type")

# Outputs: Conversion failed


# =========================================
# 1.6 Catching All Exceptions
# =========================================
"""
You can catch any exception using a general 'except' block.

However, this should be used carefully.
"""

try:
    x = 1 / 0
except Exception as e:
    print("An error occurred:", e)

# Outputs: An error occurred: division by zero


# =========================================
# 1.7 Accessing Exception Information
# =========================================
"""
You can capture the exception object for more details.
"""

try:
    int("abc")
except ValueError as e:
    print(type(e))  # Exception type
    print(e)        # Error message


# =========================================
# 1.8 Optional else and finally Blocks
# =========================================
"""
Additional blocks can be used with try/except:

- else → runs if no exception occurs
- finally → always runs
"""

try:
    result = 10 / 2
except ZeroDivisionError:
    print("Error")
else:
    print("Success:", result)
finally:
    print("Finished")

# Outputs:
# Success: 5.0
# Finished


# =========================================
# 1.9 Key Idea
# =========================================
"""
Exceptions:
- Represent runtime errors
- Prevent programs from silently failing
- Can be handled to control program flow

Tracebacks help you:
- Locate the problem
- Understand what went wrong
"""


# =========================================
# 1.10 Summary
# =========================================
"""
Exceptions provide a structured way to handle errors:

- Errors raise exceptions
- Exceptions have types and messages
- Tracebacks show where errors occur
- try/except allows recovery from errors

Key idea:
"Errors can be managed, not just avoided"
"""