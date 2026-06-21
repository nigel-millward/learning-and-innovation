# =========================================
# 1. Exception Chaining
# =========================================
"""
Exception chaining occurs when one exception is raised while handling another.

Python automatically links related exceptions together,
making debugging easier by preserving the original cause.
"""


# =========================================
# 1.1 Automatic Exception Chaining
# =========================================
"""
If an exception is raised inside an except block,
Python automatically chains it to the original exception.
"""

try:
    open("database.sqlite")
except OSError:
    raise RuntimeError("unable to handle error")


"""
Typical output:

FileNotFoundError: ...

During handling of the above exception, another exception occurred:

RuntimeError: unable to handle error

Key idea:
The new exception keeps a reference to the original one.
"""


# =========================================
# 1.2 Explicit Exception Chaining (raise ... from)
# =========================================
"""
You can explicitly link exceptions using:

raise NewException from original_exception
"""

def func():
    raise ConnectionError()


try:
    func()
except ConnectionError as exc:
    raise RuntimeError("Failed to open database") from exc


"""
Typical output:

ConnectionError

The above exception was the direct cause of the following exception:

RuntimeError: Failed to open database

This clearly indicates the relationship between errors.
"""


# =========================================
# 1.3 Why Use Exception Chaining?
# =========================================
"""
Explicit chaining is useful when:
- Transforming low-level errors into higher-level ones
- Preserving the original cause for debugging
- Improving error clarity for users
"""

def load_data():
    raise FileNotFoundError("file missing")

try:
    load_data()
except FileNotFoundError as exc:
    raise RuntimeError("Could not load application data") from exc


# =========================================
# 1.4 Disabling Exception Chaining
# =========================================
"""
You can suppress the original exception using:

raise Exception from None
"""

try:
    open("database.sqlite")
except OSError:
    raise RuntimeError("generic error") from None


"""
Output will only show:

RuntimeError: generic error

The original exception is hidden.
"""


# =========================================
# 1.5 Implicit vs Explicit Chaining
# =========================================
"""
Implicit chaining:
- Happens automatically
- Uses context information

Explicit chaining:
- Uses 'from'
- Clearly defines cause

Difference:
- Implicit → "During handling of the above exception..."
- Explicit → "The above exception was the direct cause..."
"""


# =========================================
# 1.6 Key Idea
# =========================================
"""
Exception chaining allows you to:

- Track the root cause of errors
- Convert low-level exceptions into meaningful ones
- Maintain debugging information across layers
"""


# =========================================
# 1.7 Summary
# =========================================
"""
Exception chaining provides:

- Automatic linking of related exceptions
- Explicit control using 'raise ... from'
- Optional suppression using 'from None'

Key patterns:
- raise NewError from old_error
- raise NewError from None

Core idea:
"Preserve the story of how an error happened"
"""
