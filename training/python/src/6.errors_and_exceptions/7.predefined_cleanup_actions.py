# =========================================
# 1. Predefined Clean-up Actions (with)
# =========================================
"""
Some objects define built-in clean-up behaviour.

These objects:
- Automatically release resources when they are no longer needed
- Provide a safe and structured way to manage resources

The 'with' statement is used to ensure clean-up happens reliably.
"""


# =========================================
# 1.1 The Problem Without Cleanup
# =========================================
"""
Opening resources (like files) without proper cleanup can lead to issues,
especially in larger applications.

Example:
"""

for line in open("myfile.txt"):
    print(line, end="")


"""
Problem:
- The file remains open after use
- Cleanup timing is unpredictable
- Can lead to resource leaks
"""


# =========================================
# 1.2 Using the with Statement
# =========================================
"""
The with statement ensures resources are properly cleaned up.

It automatically handles setup and cleanup.
"""

with open("myfile.txt") as f:
    for line in f:
        print(line, end="")


"""
After the block finishes:
- The file is automatically closed
- This happens even if an error occurs
"""


# =========================================
# 1.3 How with Works
# =========================================
"""
The with statement works by calling special methods:

- __enter__() → runs at the start
- __exit__() → runs at the end (cleanup)

These methods are defined by the object.
"""


# =========================================
# 1.4 Equivalent try/finally Pattern
# =========================================
"""
The with statement is equivalent to writing:

"""

f = open("myfile.txt")

try:
    for line in f:
        print(line, end="")
finally:
    f.close()


"""
Key advantage of 'with':
- Cleaner code
- Less error-prone
- Guarantees cleanup
"""


# =========================================
# 1.5 Objects That Support with
# =========================================
"""
Objects that support the with statement are called context managers.

Common examples:
- Files (open)
- Locks (threading)
- Network connections
- Database sessions

These objects define their own cleanup logic.
"""


# =========================================
# 1.6 Why Use with?
# =========================================
"""
The with statement ensures:

- Resources are always released
- Code is easier to read
- Errors do not prevent cleanup

It is the preferred way to work with external resources.
"""


# =========================================
# 1.7 Key Idea
# =========================================
"""
The with statement guarantees that:

- Setup happens before the block
- Cleanup happens after the block

No matter what happens in between.
"""


# =========================================
# 1.8 Summary
# =========================================
"""
Predefined clean-up actions allow objects to manage themselves.

The with statement:
- Simplifies resource management
- Replaces try/finally in common cases
- Ensures safe and predictable cleanup

Core idea:
"Use resources safely, and release them automatically"
"""