# =========================================
# 1. Reading and Writing Files
# =========================================
"""
Python provides built-in support for reading and writing files using open().

A file object allows you to:
- Read data from files
- Write data to files
- Manage file resources safely
"""


# =========================================
# 1.1 Opening Files
# =========================================
"""
Use open() to create a file object.

Syntax:
open(filename, mode, encoding=None)
"""

f = open("workfile.txt", "w", encoding="utf-8")

"""
Arguments:
- filename → name of the file
- mode → how the file is used
- encoding → text encoding (recommended: UTF-8)
"""


# =========================================
# 1.2 File Modes
# =========================================
"""
Common file modes:

- 'r'  → read (default)
- 'w'  → write (overwrites file)
- 'a'  → append (adds to end)
- 'r+' → read and write

Add 'b' for binary mode:
- 'rb', 'wb', etc.
"""

# Example
f = open("example.txt", "a", encoding="utf-8")


# =========================================
# 1.3 Text vs Binary Mode
# =========================================
"""
Text mode (default):
- Works with strings
- Handles line endings automatically

Binary mode ('b'):
- Works with bytes
- No encoding allowed
- Required for non-text files (e.g. images)
"""

# Binary example
# f = open("image.jpg", "rb")


# =========================================
# 1.4 Writing to Files
# =========================================
"""
Use write() to write data to a file.
"""

f = open("example.txt", "w", encoding="utf-8")

f.write("Hello, world!")
f.close()


"""
Warning:
If you do not close the file properly, data may not be fully written.
"""


# =========================================
# 1.5 Reading from Files
# =========================================
"""
Common methods for reading:

- read()      → entire file
- readline()  → one line
- readlines() → list of lines
"""

f = open("example.txt", "r", encoding="utf-8")

content = f.read()
print(content)

f.close()


# =========================================
# 1.6 Using with (Recommended)
# =========================================
"""
The 'with' statement automatically closes the file.

This is the preferred way to work with files.
"""

with open("example.txt", encoding="utf-8") as f:
    content = f.read()

print(content)


"""
After the block:
- The file is automatically closed
"""

print(f.closed)  # Outputs: True


# =========================================
# 1.7 File Closure and Errors
# =========================================
"""
Once a file is closed, it cannot be used again.
"""

f = open("example.txt", "r", encoding="utf-8")
f.close()

# f.read()  # Raises ValueError


# =========================================
# 1.8 Iterating Over Files
# =========================================
"""
Files are iterable objects.

You can loop through them line by line.
"""

with open("example.txt", encoding="utf-8") as f:
    for line in f:
        print(line, end="")


# =========================================
# 1.9 Line Ending Handling
# =========================================
"""
In text mode:

- Reading converts line endings to '\n'
- Writing converts '\n' to platform-specific endings

This is useful for text files but incorrect for binary data.
"""


# =========================================
# 1.10 Best Practices
# =========================================
"""
- Always use 'with' when opening files
- Specify encoding="utf-8"
- Use text mode for text, binary mode for binary data
- Close files properly if not using 'with'
"""


# =========================================
# 1.11 Key Idea
# =========================================
"""
File handling allows programs to:

- Persist data to disk
- Load external data
- Process large datasets

Using 'with' ensures safe and reliable file access.
"""


# =========================================
# 1.12 Summary
# =========================================
"""
Reading and writing files involves:

- open() → create file object
- read()/write() → interact with file
- close() → release resources

Best practice:
Use 'with' to guarantee cleanup.

Core idea:
"Open, use, and safely close files"
"""