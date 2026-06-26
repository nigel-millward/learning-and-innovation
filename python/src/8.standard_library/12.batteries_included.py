# =========================================
# 1. Operating System Interface (os)
# =========================================
"""
Python provides the os module to interact with the operating system.

It allows you to:
- Work with files and directories
- Run system commands
- Inspect the environment

This is essential for automation and system-level tasks.
"""


# =========================================
# 1.1 Importing the os Module
# =========================================
"""
Always import the os module using:

import os

Avoid:
from os import *

This prevents name conflicts (e.g. os.open vs built-in open()).
"""

import os


# =========================================
# 1.2 Getting and Changing Directories
# =========================================
"""
Common directory operations:
"""

# Current working directory
cwd = os.getcwd()
print(cwd)

# Change directory
# os.chdir("/server/accesslogs")


"""
getcwd() → returns current directory
chdir(path) → changes current directory
"""


# =========================================
# 1.3 Running System Commands
# =========================================
"""
You can run shell commands using os.system().
"""

# os.system("mkdir today")

"""
Returns:
- Exit status of the command (0 usually means success)

Note:
- This runs commands in the system shell
- Use carefully for security reasons
"""


# =========================================
# 1.4 Exploring the os Module
# =========================================
"""
The os module contains many functions.

Use built-in tools to explore it:
"""

print(dir(os))   # List all attributes

help(os)         # Show documentation


"""
Useful for:
- Discovering features
- Understanding function behaviour
"""


# =========================================
# 1.5 High-Level File Operations (shutil)
# =========================================
"""
The shutil module provides simpler, higher-level file operations.

It is often easier than using os directly.
"""

import shutil

# Copy a file
# shutil.copyfile("data.db", "archive.db")

# Move a file or directory
# shutil.move("/build/executables", "installdir")


"""
shutil is recommended for:
- Copying files
- Moving files/directories
- Managing file structures
"""


# =========================================
# 1.6 Common Use Cases
# =========================================
"""
The os and shutil modules are commonly used for:

- File and directory management
- Automation scripts
- Deployment tasks
- System interaction
"""


# =========================================
# 1.7 Key Idea
# =========================================
"""
The os module provides low-level access to the operating system.

The shutil module provides higher-level, easier-to-use tools.

Use:
- os → for system-level control
- shutil → for file operations
"""


# =========================================
# 1.8 Summary
# =========================================
"""
Core tools:

- os.getcwd() → current directory
- os.chdir(path) → change directory
- os.system(cmd) → run command
- dir(os), help(os) → explore module

High-level tools:
- shutil.copyfile()
- shutil.move()

Best practices:
- Use 'import os' (not wildcard imports)
- Prefer shutil for file management
- Use system commands carefully

Core idea:
"Interact with the operating system safely and effectively"
"""
