# =========================================
# 1. Reading and Writing Files
# =========================================
"""
Python provides built-in support for reading and writing files.

The 'with' statement is the standard way to open files safely.
It guarantees the file is closed when the block finishes —
even if an exception occurs.

This module covers:
- Opening files with 'with'
- Reading files (whole file, line by line, readlines)
- Writing and appending to files
- Working with file modes
- Why 'with' is preferred over manual open/close
"""


# =========================================
# 1.1 The Problem Without 'with'
# =========================================
"""
Opening a file manually requires explicit closing.

If an exception occurs before f.close(), the file stays open.
This can cause resource leaks in long-running programs.
"""

# f = open("data.txt")
# content = f.read()
# f.close()   # May never be reached if an error occurs above


# =========================================
# 1.2 Opening Files Safely with 'with'
# =========================================
"""
The 'with' statement handles opening and closing automatically.

Syntax:
    with open(filename, mode) as f:
        ...

The file is closed when the block ends — even on error.
"""

# with open("data.txt") as f:
#     content = f.read()
# File is now closed, even if f.read() raised an exception


# =========================================
# 1.3 File Modes
# =========================================
"""
The mode argument controls how the file is opened.

Common modes:

Mode  | Description
------|------------------------------
'r'   | Read (default)
'w'   | Write (creates or overwrites)
'a'   | Append (adds to end of file)
'x'   | Exclusive create (fails if exists)
'rb'  | Read binary
'wb'  | Write binary

If mode is omitted, 'r' is assumed.
"""


# =========================================
# 1.4 Reading an Entire File
# =========================================
"""
f.read() returns the entire file contents as a single string.
"""

# with open("data.txt", "r") as f:
#     content = f.read()
#     print(content)


# =========================================
# 1.5 Reading Line by Line
# =========================================
"""
Iterating over a file object reads one line at a time.

This is memory-efficient for large files — the whole file
is not loaded into memory at once.
"""

# with open("data.txt", "r") as f:
#     for line in f:
#         print(line, end="")  # lines include '\n', end="" avoids double spacing


# =========================================
# 1.6 Reading All Lines into a List
# =========================================
"""
f.readlines() returns a list where each element is a line (including '\n').

Useful when you need random access to lines.
"""

# with open("data.txt", "r") as f:
#     lines = f.readlines()
#     print(lines[0])  # First line


# =========================================
# 1.7 Writing to a File
# =========================================
"""
Open with mode 'w' to write.

Warning: 'w' overwrites the file if it already exists.
"""

with open("output.txt", "w") as f:
    f.write("Hello, world!\n")
    f.write("Second line\n")

# output.txt now contains:
# Hello, world!
# Second line


# =========================================
# 1.8 Appending to a File
# =========================================
"""
Open with mode 'a' to add content without overwriting.
"""

with open("output.txt", "a") as f:
    f.write("Third line\n")

# output.txt now contains:
# Hello, world!
# Second line
# Third line


# =========================================
# 1.9 Reading Back What We Wrote
# =========================================
"""
Read the file back to verify the contents.
"""

with open("output.txt", "r") as f:
    for line in f:
        print(line, end="")

# Hello, world!
# Second line
# Third line


# =========================================
# 1.10 Multiple Files with 'with'
# =========================================
"""
You can open multiple files in a single 'with' statement.

Useful for copying or transforming file content.
"""

# with open("input.txt", "r") as source, open("output.txt", "w") as dest:
#     for line in source:
#         dest.write(line.upper())


# =========================================
# 1.11 How 'with' Works Under the Hood
# =========================================
"""
'with' works via the context manager protocol:

- __enter__() is called when the block starts  → returns the file object
- __exit__() is called when the block ends     → closes the file

This is equivalent to:

    f = open("data.txt")
    try:
        content = f.read()
    finally:
        f.close()   # always runs

'with' is cleaner, shorter, and less error-prone.

See: 6.errors_and_exceptions/7.predefined_cleanup_actions.py
     7.classes/12.dunder_methods.py  (for __enter__ / __exit__)
"""


# =========================================
# 1.12 Key Idea
# =========================================
"""
Always use 'with' when working with files.

It guarantees:
- The file is always closed
- Resources are not leaked
- Code is clean and readable
"""


# =========================================
# 1.13 Summary
# =========================================
"""
Reading and writing files:

    with open("file.txt", "r") as f:   # read
        content = f.read()

    with open("file.txt", "w") as f:   # write (overwrites)
        f.write("text")

    with open("file.txt", "a") as f:   # append
        f.write("more text")

Key methods:
- f.read()       → full file as a string
- f.readlines()  → list of lines
- for line in f  → iterate line by line (memory efficient)
- f.write(text)  → write a string

Core idea:
"Always open files with 'with' — it handles cleanup for you"
"""
