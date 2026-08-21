# =========================================
# 1. Error Output and Program Termination
# =========================================
"""
Python programs interact with three standard streams:

- stdin  → input (e.g. keyboard)
- stdout → normal output (e.g. print)
- stderr → error and warning output

The sys module provides access to these streams.
"""


# =========================================
# 1.1 Standard Output vs Error Output
# =========================================
"""
Normal output is written to stdout using print().

Error messages should be written to stderr.
"""

import sys

print("This is normal output")  # goes to stdout

sys.stderr.write("This is an error message\n")  # goes to stderr


"""
Example output:

This is normal output
This is an error message
"""


# =========================================
# 1.2 Why Use stderr?
# =========================================
"""
stderr is useful because:

- It separates errors from normal output
- It remains visible even if stdout is redirected

Example:
python script.py > output.txt

- print() output → output.txt
- stderr output → still shown in terminal
"""


# =========================================
# 1.3 Writing to stderr
# =========================================
"""
Use sys.stderr.write() to send messages to stderr.

Note:
- It does NOT automatically add a newline
"""

import sys

sys.stderr.write("Warning: log file not found\n")


# =========================================
# 1.4 Program Termination (sys.exit)
# =========================================
"""
Use sys.exit() to terminate a program immediately.
"""

import sys

# sys.exit()


"""
You can pass values to sys.exit():
"""

# sys.exit(0)       → success
# sys.exit(1)       → error
# sys.exit("Error") → prints message and exits


# =========================================
# 1.5 Exit Codes
# =========================================
"""
Exit codes indicate program status:

- 0 → success
- non-zero → error

These are useful for:
- shell scripts
- automation tools
"""


# =========================================
# 1.6 Example: Combining stderr and exit
# =========================================
"""
Typical pattern for handling errors in scripts:
"""

import sys

def process_file(filename):
    if filename == "":
        sys.stderr.write("Error: filename is required\n")
        sys.exit(1)

process_file("")


# =========================================
# 1.7 Key Idea
# =========================================
"""
Use separate output streams:

- stdout → normal program output
- stderr → warnings and errors

Control program termination using sys.exit().
"""


# =========================================
# 1.8 Summary
# =========================================
"""
Core tools:

- sys.stderr.write() → write error messages
- sys.exit() → terminate program

Best practices:
- Send errors to stderr
- Use exit codes for automation
- Keep output streams separate

Core idea:
"Separate normal output from errors and control program termination"
"""
