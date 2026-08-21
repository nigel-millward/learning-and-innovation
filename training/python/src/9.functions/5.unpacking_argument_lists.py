# =========================================
# 1. Unpacking Argument Lists
# =========================================
"""
Sometimes arguments are already in a list or tuple but need to be unpacked for a function call
requiring separate positional arguments.

This module covers:
- Unpacking lists with *
- Unpacking dictionaries with **
"""


# =========================================
# 1.1 Unpacking Lists
# =========================================
"""
Use the * operator to unpack a list or tuple into separate positional arguments.
"""

args = [3,6]
list(range(*args))  # [0, 1, 2, 3, 4, 5]


# =========================================
# 1.2 Unpacking Dictionaries
# =========================================
"""
Use the ** operator to unpack a dictionary into separate keyword arguments.
"""

def parrot(voltage, state='a stiff', action='voom'):
    print("-- This parrot wouldn't", action, end=' ')
    print("if you put", voltage, "volts through it.", end=' ')
    print("E's", state, "!")

d = {"voltage": "four million", "state": "bleedin' demised", "action": "VOOOOM"}
parrot(**d)
