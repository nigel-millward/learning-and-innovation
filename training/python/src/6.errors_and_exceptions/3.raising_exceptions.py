# =========================================
# 1. Raising Exceptions
# =========================================
"""
The raise statement allows you to trigger an exception manually.

This is useful when:
- You detect an invalid condition
- You want to enforce rules in your program
- You need to signal an error intentionally
"""


# =========================================
# 1.1 Raising an Exception Instance
# =========================================
"""
You can raise an exception by creating an instance.
"""

raise NameError("HiThere")

# Output:
# NameError: HiThere


# =========================================
# 1.2 Raising an Exception Class
# =========================================
"""
You can also raise an exception class directly.

Python will automatically instantiate it.
"""

raise ValueError  # Equivalent to: raise ValueError()

# Output:
# ValueError


# =========================================
# 1.3 Raising Exceptions in Practice
# =========================================
"""
raise is often used to enforce rules and validate inputs.
"""

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# print(divide(10, 0))  # Raises ValueError


# =========================================
# 1.4 Re-raising Exceptions
# =========================================
"""
You can catch an exception and then raise it again.

This allows you to:
- Perform some action (e.g. logging)
- Let the error continue upward
"""

try:
    raise NameError("HiThere")
except NameError:
    print("An exception flew by!")
    raise


# Output:
# An exception flew by!
# NameError: HiThere


# =========================================
# 1.5 Why Re-raise Exceptions?
# =========================================
"""
Re-raising is useful when:
- You want to log or inspect the error
- You cannot fully handle it at the current level
- You want higher-level code to decide what to do
"""

# load_config is low-level — it handles a specific technical task (reading a file).
def load_config(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"[load_config] Config not found at '{path}', re-raising...")
        raise  # Let the caller decide how to handle the missing file. In this example, it will be caught by start_app.

# start_app is high-level — it orchestrates the application startup 
# and knows what to do when things go wrong (fall back to defaults).
def start_app(config_path):
    try:
        config = load_config(config_path)
        print("App started with config:", config)
    except FileNotFoundError:
        # Higher-level code decides: fall back to defaults instead of crashing
        print("[start_app] No config found — starting with default settings.")

# start_app("config.yaml")
# Output:
# [load_config] Config not found at 'config.yaml', re-raising...
# [start_app] No config found — starting with default settings.


# =========================================
# 1.6 Custom Error Conditions
# =========================================
"""
You can define your own conditions and raise appropriate exceptions.

Choose exception types carefully to match the error.
"""

def withdraw(balance, amount):
    if amount > balance:
        raise ValueError("Insufficient funds")
    return balance - amount


# =========================================
# 1.7 Key Idea
# =========================================
"""
raise allows you to:

- Signal errors explicitly
- Enforce constraints in your code
- Integrate with Python's exception system

It gives you control over when and how errors occur.
"""


# =========================================
# 1.8 Summary
# =========================================
"""
Raising exceptions involves:

- raise ExceptionType("message")
- raise ExceptionType (auto-instantiated)
- raise (to re-raise current exception)

Key practices:
- Raise meaningful errors
- Use appropriate exception types
- Re-raise when needed

Core idea:
"Make errors explicit and intentional"
"""