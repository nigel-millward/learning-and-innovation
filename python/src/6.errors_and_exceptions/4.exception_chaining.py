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
Traceback (most recent call last):
  File "4.exception_chaining.py", line 20, in <module>
    open("database.sqlite")
FileNotFoundError: [Errno 2] No such file or directory: 'database.sqlite'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "4.exception_chaining.py", line 22, in <module>
    raise RuntimeError("unable to handle error")
RuntimeError: unable to handle error

Key idea:
The new exception keeps a reference to the original one.

RuntimeError (bottom, line 37) is what ultimately failed — what went wrong
FileNotFoundError (top, line 30) is the root cause — why it went wrong

FileNotFoundError caused RuntimeError
The chain flows: FileNotFoundError happened first → while handling it, RuntimeError was raised.

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
Traceback (most recent call last):
  File "4.exception_chaining.py", line 43, in <module>
    func()
  File "4.exception_chaining.py", line 41, in func
    raise ConnectionError()
ConnectionError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "4.exception_chaining.py", line 45, in <module>
    raise RuntimeError("Failed to open database") from exc
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

"""
Traceback (most recent call last):
  File "4.exception_chaining.py", line 62, in <module>
    load_data()
  File "4.exception_chaining.py", line 60, in load_data
    raise FileNotFoundError("file missing")
FileNotFoundError: file missing

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "4.exception_chaining.py", line 64, in <module>
    raise RuntimeError("Could not load application data") from exc
RuntimeError: Could not load application data
"""


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
Traceback (most recent call last):
  File "4.exception_chaining.py", line 75, in <module>
    raise RuntimeError("generic error") from None
RuntimeError: generic error

The original FileNotFoundError is completely hidden — only the final error is shown.
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
