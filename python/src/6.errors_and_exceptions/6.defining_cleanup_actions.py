# =========================================
# 1. Clean-up Actions (finally)
# =========================================
"""
The try statement supports a finally clause.

The finally block defines clean-up actions that must run:
- Whether an exception occurs or not
- Before the try statement fully completes

This ensures important tasks are always performed.
"""


def run_demo(title, func):
    print(f"\n--- {title} ---")
    try:
        func()
    except Exception as exc:
        print(f"Unhandled exception propagated: {type(exc).__name__}: {exc}")
    except BaseException as exc:
        # KeyboardInterrupt inherits from BaseException, not Exception.
        print(f"Unhandled base exception propagated: {type(exc).__name__}")


# =========================================
# 1.1 Basic finally Usage
# =========================================
"""
The finally block always runs, even if an exception occurs.
"""


def demo_basic_finally_usage():
    try:
        raise KeyboardInterrupt
    finally:
        print("Goodbye, world!")


# Output:
# Goodbye, world!
# KeyboardInterrupt (propagates)


# =========================================
# 1.2 Execution Order
# =========================================
"""
The order of execution is:

1. try block runs
2. If an exception occurs:
   - except block may handle it
3. finally block always runs last

If the exception is not handled:
- It is re-raised after finally executes
"""


# =========================================
# 1.3 finally with try/except
# =========================================
"""
The finally block runs whether or not an exception is handled.
"""

def divide(x, y):
    try:
        result = x / y
    except ZeroDivisionError:
        print("division by zero!")
    else:
        print("result is", result)
    finally:
        print("executing finally clause")


def demo_finally_with_try_except():
    divide(2, 1)
    # Outputs:
    # result is 2.0
    # executing finally clause

    divide(2, 0)
    # Outputs:
    # division by zero!
    # executing finally clause


# =========================================
# 1.4 Unhandled Exceptions and finally
# =========================================
"""
If an exception is not handled, it is still re-raised after finally runs.
"""


def demo_unhandled_exception_and_finally():
    divide("2", "1")

# Outputs:
# executing finally clause
# TypeError ...


# =========================================
# 1.5 finally with return Statements
# =========================================
"""
The finally block still runs even if the try block returns a value.
"""

def example():
    try:
        return True
    finally:
        print("Running finally")


def demo_finally_with_return():
    print(example())

# Outputs:
# Running finally
# True


# =========================================
# 1.6 Important Caution: return in finally
# =========================================
"""
A return statement inside finally overrides any previous return.

This behaviour is discouraged because it is confusing.
Some IDEs/linters also flag this pattern as an error.
"""

def bool_return():
    try:
        return True
    finally:
        # Keep finally for cleanup only; avoid changing control flow here.
        print("Cleanup in finally")


def demo_caution_return_in_finally():
    print(bool_return())  # Outputs: Cleanup in finally, then True


# =========================================
# 1.7 break, continue, and finally
# =========================================
"""
If break, continue, or return are used:

- finally executes before the control flow changes
- Using them inside finally can suppress exceptions

This behaviour can be confusing and should be avoided.
"""


# =========================================
# 1.8 Real-World Use: Resource Cleanup
# =========================================
"""
The main use of finally is to release resources.

Examples:
- Closing files
- Closing network connections
- Releasing locks
"""

def demo_resource_cleanup():
    f = open("example.txt", "w")
    try:
        f.write("Hello")
    finally:
        f.close()


# =========================================
# 1.9 Key Idea
# =========================================
"""
The finally block guarantees execution.

It is used to:
- Clean up resources
- Maintain system consistency
- Ensure important actions always happen
"""


# =========================================
# 1.10 Summary
# =========================================
"""
The finally clause:

- Always runs after try/except/else
- Executes even if an exception occurs
- Runs before exceptions are re-raised

Best practices:
- Use finally for cleanup actions
- Avoid return/break/continue inside finally

Core idea:
"Always leave things in a safe and consistent state"
"""


if __name__ == "__main__":
    run_demo("1.1 Basic finally Usage", demo_basic_finally_usage)
    run_demo("1.3 finally with try/except", demo_finally_with_try_except)
    run_demo("1.4 Unhandled Exceptions and finally", demo_unhandled_exception_and_finally)
    run_demo("1.5 finally with return Statements", demo_finally_with_return)
    run_demo("1.6 Important Caution: return in finally", demo_caution_return_in_finally)
    run_demo("1.8 Real-World Use: Resource Cleanup", demo_resource_cleanup)