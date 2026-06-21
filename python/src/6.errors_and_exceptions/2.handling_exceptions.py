# =========================================
# 1. Handling Exceptions
# =========================================
"""
Programs can handle exceptions to avoid crashing and respond to errors gracefully.

Use try/except blocks to:
- Catch specific errors
- Control program flow
- Allow recovery from failures
"""


# =========================================
# 1.1 Basic try/except Workflow
# =========================================
"""
The try statement works as follows:

1. The try block is executed
2. If no exception occurs → skip except block
3. If an exception occurs:
   - Remaining try code is skipped
   - Matching except block is executed
"""

try:
    x = int("123")
except ValueError:
    print("Conversion failed")

# Outputs nothing (no error occurred)


# =========================================
# 1.2 Handling User Input Safely
# =========================================
"""
A common pattern is to repeat input until it is valid.
"""

while True:
    try:
        x = int(input("Please enter a number: "))
        break
    except ValueError:
        print("Oops! That was not a valid number. Try again...")


# =========================================
# 1.3 Unmatched Exceptions
# =========================================
"""
If an exception does not match any except clause:

- It is passed to outer try blocks
- If unhandled, the program stops with an error
"""

try:
    x = 1 / 0
except ValueError:
    print("Handled ValueError")

# ZeroDivisionError is not handled → program crashes


# =========================================
# 1.4 Multiple except Clauses
# =========================================
"""
You can handle different exception types separately.

Only the first matching except block is executed.
"""

try:
    x = int("abc")
except ValueError:
    print("ValueError occurred")
except TypeError:
    print("TypeError occurred")

# Outputs: ValueError occurred


# =========================================
# 1.5 Handling Multiple Exceptions Together
# =========================================
"""
You can group multiple exception types in one except clause.
"""

try:
    x = int("abc")
except (ValueError, TypeError, NameError):
    print("Handled multiple possible errors")


# =========================================
# 1.6 Exception Hierarchy (Order Matters)
# =========================================
"""
Exceptions follow an inheritance hierarchy.

More specific exceptions should be placed first.
"""

class B(Exception):
    pass

class C(B):
    pass

class D(C):
    pass

for cls in [B, C, D]:
    try:
        raise cls()
    except D:
        print("D")
    except C:
        print("C")
    except B:
        print("B")

# Outputs:
# B
# C
# D


"""
If reversed, the first match would always be used.
"""


# =========================================
# 1.7 Exception Objects and Arguments
# =========================================
"""
Exceptions are objects and may contain additional data (arguments).
"""

try:
    raise Exception("spam", "eggs")
except Exception as inst:
    print(type(inst))   # exception type
    print(inst.args)    # stored arguments
    print(inst)         # string representation

    x, y = inst.args
    print("x =", x)
    print("y =", y)

# Outputs:
# <class 'Exception'>
# ('spam', 'eggs')
# ('spam', 'eggs')
# x = spam
# y = eggs


# =========================================
# 1.8 Catching General Exceptions
# =========================================
"""
Exception is the base class for most non-fatal errors.

It can be used as a catch-all, but should be used carefully.
"""

try:
    x = 1 / 0
except Exception as err:
    print("Error:", err)


"""
Avoid catching everything unless necessary.
Prefer specific exception types.
"""


# =========================================
# 1.9 Re-raising Exceptions
# =========================================
"""
You can handle an exception and then re-raise it.

This allows:
- Logging or debugging
- Passing the error to higher-level code
"""

try:
    x = int("abc")
except ValueError as err:
    print("Logging error:", err)
    raise  # re-raise exception


# =========================================
# 1.10 try/except/else
# =========================================
"""
The else block runs only if no exception occurs.

This keeps the try block focused on risky code.
"""

try:
    x = int("10")
except ValueError:
    print("Error")
else:
    print("Success:", x)

# Outputs: Success: 10


# =========================================
# 1.11 try/except/finally
# =========================================
"""
The finally block runs no matter what.

Useful for:
- Closing files
- Releasing resources
"""

try:
    x = 10 / 2
except ZeroDivisionError:
    print("Error")
finally:
    print("Cleaning up")

# Outputs:
# Cleaning up


# =========================================
# 1.12 Exceptions in Function Calls
# =========================================
"""
Exceptions raised inside functions are also caught by try/except.
"""

def this_fails():
    return 1 / 0

try:
    this_fails()
except ZeroDivisionError as err:
    print("Handled run-time error:", err)

# Outputs: Handled run-time error: division by zero


# =========================================
# 1.13 Key Idea
# =========================================
"""
Exception handling allows programs to:

- Recover from expected errors
- Control failure behaviour
- Separate normal logic from error handling

Write code that:
- Handles known problems
- Allows unexpected ones to propagate
"""


# =========================================
# 1.14 Summary
# =========================================
"""
Handling exceptions involves:

- try → code that may fail
- except → handle specific errors
- else → runs if no error occurs
- finally → always runs

Key practices:
- Catch specific exceptions
- Order handlers correctly
- Re-raise when appropriate

Core idea:
"Fail safely, and recover where possible"
"""