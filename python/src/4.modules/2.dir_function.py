# =========================================
# 1. The dir() Function
# =========================================
"""
The built-in dir() function is used to find out which names a module or scope defines.

This section covers:
- Using dir() to list the names a module defines
- Using dir() without arguments to list names in the current local scope
- Using dir() on builtins to list built-in functions and variables
"""


# =========================================
# 1.1 Listing the Names a Module Defines
# =========================================
"""
The built-in function dir() is used to find out which names a module defines.
"""

import fibo, sys
dir(fibo)
"""
['__name__', 'fib', 'fib2']
"""

dir(sys)


# =========================================
# 1.2 dir() Without Arguments
# =========================================
"""
dir() without arguments lists the names of the current local scope.
"""

a = [1, 2, 3, 4, 5]
import fibo
fib = fibo.fib
dir()
"""
['__builtins__', '__name__', 'a', 'fib', 'fibo', 'sys']
"""


# =========================================
# 1.3 Listing Built-in Names
# =========================================
"""
builtins lists the names of built-in functions and variables.
"""

import builtins
dir(builtins)
