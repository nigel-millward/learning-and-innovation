# =========================================
# 1. Enriching Exceptions with Notes
# =========================================
"""
Exceptions can carry additional information beyond their original message.

Python provides the add_note() method to attach extra context
to an exception after it has been raised and caught.

This is useful when:
- Adding context to errors at different layers
- Providing debugging information
- Tracking where and why errors occurred
"""


def run_demo(title, func):
    print(f"\n--- {title} ---")
    try:
        func()
    except Exception as exc:
        print(f"Unhandled exception propagated: {type(exc).__name__}: {exc}")


# =========================================
# 1.1 Adding Notes to Exceptions
# =========================================
"""
The add_note() method adds a string to an exception's notes list.

These notes are displayed in the traceback.
"""


def demo_adding_notes_to_exceptions():
    try:
        raise TypeError("bad type")
    except Exception as e:
        e.add_note("Add some information")
        e.add_note("Add some more information")
        raise


"""
Typical output:

TypeError: bad type
Add some information
Add some more information

Notes appear after the main exception message.
"""


# =========================================
# 1.2 Why Use Notes?
# =========================================
"""
Notes allow you to:

- Add context after catching an exception
- Keep the original exception unchanged
- Improve debugging without modifying the exception type

This is especially useful in layered systems.
"""


# =========================================
# 1.3 Adding Context in Loops
# =========================================
"""
Notes are useful for identifying which iteration or step failed.
"""

def f():
    raise OSError("operation failed")


def demo_adding_context_in_loops():
    excs = []

    for i in range(3):
        try:
            f()
        except Exception as e:
            e.add_note(f"Happened in iteration {i + 1}")
            excs.append(e)

    raise ExceptionGroup("We have some problems", excs)


"""
Each exception now includes its own context:

OSError: operation failed
Happened in iteration 1

OSError: operation failed
Happened in iteration 2

OSError: operation failed
Happened in iteration 3
"""


# =========================================
# 1.4 Notes with Exception Groups
# =========================================
"""
When used with ExceptionGroup:

- Each exception can carry its own notes
- Notes are preserved and displayed individually
- This provides detailed insight into multiple failures
"""


# =========================================
# 1.5 Key Idea
# =========================================
"""
add_note() allows you to:

- Enrich exceptions with additional context
- Improve error messages without changing exception types
- Track where and how errors occurred

It complements exception chaining and grouping.
"""


# =========================================
# 1.6 Summary
# =========================================
"""
Enriching exceptions involves:

- Using add_note("message") to attach context
- Adding notes after catching an exception
- Using notes to improve debugging clarity

Best practices:
- Keep notes concise and informative
- Add context that helps locate the problem
- Use alongside ExceptionGroup for detailed reporting

Core idea:
"Add context to errors without losing the original exception"
"""


if __name__ == "__main__":
    run_demo("1.1 Adding Notes to Exceptions", demo_adding_notes_to_exceptions)
    run_demo("1.3 Adding Context in Loops", demo_adding_context_in_loops)