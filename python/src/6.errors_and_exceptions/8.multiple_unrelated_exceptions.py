# =========================================
# 1. Handling Multiple Exceptions (ExceptionGroup)
# =========================================
"""
Sometimes multiple errors can occur at the same time.

This is common in:
- concurrent programs (threads, async tasks)
- batch processing (running many operations)
- validation systems (collecting multiple failures)

Python provides ExceptionGroup to handle multiple exceptions together.
"""


# =========================================
# 1.1 Raising Multiple Exceptions
# =========================================
"""
ExceptionGroup allows you to group several exceptions into one.

It behaves like a normal exception.
"""

def f():
    excs = [
        OSError("error 1"),
        SystemError("error 2")
    ]
    raise ExceptionGroup("there were problems", excs)


# f()


"""
Typical output:

ExceptionGroup: there were problems (2 sub-exceptions)

- OSError: error 1
- SystemError: error 2
"""


# =========================================
# 1.2 Catching ExceptionGroup
# =========================================
"""
ExceptionGroup can be caught like any other exception.
"""

try:
    f()
except Exception as e:
    print(f"caught {type(e)}:", e)

# Outputs:
# caught <class 'ExceptionGroup'>: there were problems (2 sub-exceptions)


# =========================================
# 1.3 Selective Handling (except*)
# =========================================
"""
Use 'except*' to handle specific exception types inside a group.

Each clause handles matching exceptions, while others continue.
"""

def f():
    raise ExceptionGroup(
        "group1",
        [
            OSError(1),
            SystemError(2)
        ]
    )


try:
    f()
except* OSError:
    print("There were OSErrors")
except* SystemError:
    print("There were SystemErrors")

# Outputs:
# There were OSErrors
# There were SystemErrors


# =========================================
# 1.4 Nested Exception Groups
# =========================================
"""
Exception groups can contain other exception groups.
"""

def f():
    raise ExceptionGroup(
        "group1",
        [
            OSError(1),
            SystemError(2),
            ExceptionGroup(
                "group2",
                [
                    OSError(3),
                    RecursionError(4)
                ]
            )
        ]
    )


try:
    f()
except* OSError:
    print("There were OSErrors")
except* SystemError:
    print("There were SystemErrors")

# Remaining exceptions (e.g. RecursionError) are re-raised


# =========================================
# 1.5 Collecting Exceptions in Practice
# =========================================
"""
A common pattern is to collect exceptions and raise them together.
"""

class Test:
    def __init__(self, name, fail=False):
        self.name = name
        self.fail = fail

    def run(self):
        if self.fail:
            raise ValueError(f"{self.name} failed")


tests = [Test("A", True), Test("B", False), Test("C", True)]

excs = []

for test in tests:
    try:
        test.run()
    except Exception as e:
        excs.append(e)

if excs:
    raise ExceptionGroup("Test Failures", excs)


# =========================================
# 1.6 Important Rule: Exception Instances
# =========================================
"""
ExceptionGroup must contain exception instances, not classes.

Correct:
    ValueError("error")

Incorrect:
    ValueError
"""


# =========================================
# 1.7 Key Idea
# =========================================
"""
ExceptionGroup allows you to:

- Represent multiple failures as one exception
- Handle subsets of errors using except*
- Preserve all error information

This is essential for:
- concurrent systems
- batch processing
- complex workflows
"""


# =========================================
# 1.8 Summary
# =========================================
"""
Handling multiple exceptions involves:

- ExceptionGroup → group multiple errors
- except* → selectively handle types
- nested groups → represent complex failures

Key concepts:
- One exception can contain many failures
- Each type can be handled independently
- Unhandled exceptions are propagated

Core idea:
"Capture and manage multiple failures together"
"""