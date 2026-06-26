# =========================================
# 1. Command-line Arguments
# =========================================
"""
Command-line arguments allow you to pass input into a Python script
when it is run from the terminal.

This is commonly used for:
- Utility scripts
- Data processing tools
- Automation tasks
"""


# =========================================
# 1.1 Accessing Arguments with sys.argv
# =========================================
"""
The sys module provides access to command-line arguments via sys.argv.

sys.argv is a list:
- First element → script name
- Remaining elements → arguments
"""

import sys

print(sys.argv)


"""
Example:

Running:
python demo.py one two three

Output:
['demo.py', 'one', 'two', 'three']
"""


# =========================================
# 1.2 Basic Argument Processing
# =========================================
"""
You can manually access arguments using list indexing.
"""

import sys

if len(sys.argv) > 1:
    print("First argument:", sys.argv[1])


"""
Note:
- sys.argv values are always strings
"""


# =========================================
# 1.3 Limitations of sys.argv
# =========================================
"""
Using sys.argv directly can be:
- Error-prone
- Difficult to scale
- Hard to validate inputs

For more complex scripts, use argparse.
"""


# =========================================
# 1.4 Using argparse (Recommended)
# =========================================
"""
The argparse module provides structured argument parsing.

It allows:
- Named arguments
- Default values
- Type checking
- Help messages
"""

import argparse

parser = argparse.ArgumentParser(
    prog="top",
    description="Show top lines from each file"
)

parser.add_argument("filenames", nargs="+")
parser.add_argument("-l", "--lines", type=int, default=10)

args = parser.parse_args()

print(args)


"""
Example:

Running:
python top.py --lines=5 alpha.txt beta.txt

Results:
args.lines = 5
args.filenames = ['alpha.txt', 'beta.txt']
"""


# =========================================
# 1.5 Positional vs Optional Arguments
# =========================================
"""
Positional arguments:
- Required
- Defined without dashes
- Example: filenames

Optional arguments:
- Use '-' or '--'
- Have default values
- Example: -l / --lines
"""


# =========================================
# 1.6 Argument Features
# =========================================
"""
argparse provides many useful features:

- Default values
- Type conversion
- Validation
- Automatic help generation
"""

# Example: running with --help
# python top.py --help


# =========================================
# 1.7 Common Use Cases
# =========================================
"""
Command-line arguments are used for:

- File processing tools
- Data pipelines
- CLI utilities
- Automation scripts
"""


# =========================================
# 1.8 Key Idea
# =========================================
"""
Command-line arguments allow programs to:

- Accept dynamic input
- Be reused with different data
- Integrate into shell workflows

argparse makes this robust and user-friendly.
"""


# =========================================
# 1.9 Summary
# =========================================
"""
Core tools:

- sys.argv → simple argument access
- argparse → structured argument parsing

Best practices:
- Use sys.argv for simple scripts
- Use argparse for anything non-trivial

Core idea:
"Make scripts flexible by accepting input from the command line"
"""