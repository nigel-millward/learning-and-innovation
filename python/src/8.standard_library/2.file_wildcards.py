# =========================================
# 1. File Wildcards (glob)
# =========================================
"""
The glob module provides a way to search for files using wildcard patterns.

It allows you to:
- Find files matching a pattern
- Work with groups of files easily
- Avoid manually listing files
"""


# =========================================
# 1.1 Basic Usage
# =========================================
"""
Use glob.glob() to return a list of matching file names.
"""

import glob

files = glob.glob("*.py")

print(files)
# Example output: ['primes.py', 'random.py', 'quote.py']


"""
The pattern "*.py" means:
- "*" → match any characters
- ".py" → files ending in .py
"""


# =========================================
# 1.2 Common Wildcards
# =========================================
"""
glob supports standard wildcard patterns:

- *     → matches any number of characters
- ?     → matches a single character
- [abc] → matches one character from a set
"""

# Examples
print(glob.glob("file?.txt"))   # file1.txt, fileA.txt
print(glob.glob("data*.csv"))   # data1.csv, data_backup.csv
print(glob.glob("image[0-9].png"))  # image1.png, image2.png


# =========================================
# 1.3 Searching in Directories
# =========================================
"""
You can include directory paths in patterns.
"""

print(glob.glob("logs/*.txt"))
# Finds all .txt files inside the logs directory


# =========================================
# 1.4 Recursive Search
# =========================================
"""
Use '**' with recursive=True to search subdirectories.
"""

print(glob.glob("**/*.py", recursive=True))
# Finds all Python files in current directory and subdirectories


# =========================================
# 1.5 When to Use glob
# =========================================
"""
glob is useful when:
- Processing multiple files
- Automating scripts
- Working with file patterns
"""

# Example: process all CSV files
for filename in glob.glob("*.csv"):
    print(f"Processing {filename}")


# =========================================
# 1.6 Key Idea
# =========================================
"""
glob allows you to:

- Match files using patterns
- Work with groups of files dynamically
- Avoid hardcoding file names
"""


# =========================================
# 1.7 Summary
# =========================================
"""
Core usage:

- glob.glob(pattern) → returns matching file names

Common patterns:
- *.py → all Python files
- file?.txt → single-character match
- data* → prefix match

Advanced:
- ** → recursive matching (with recursive=True)

Core idea:
"Find files using patterns instead of fixed names"
"""