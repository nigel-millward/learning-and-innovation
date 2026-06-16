# =========================================
# 1. Modules
# =========================================
"""
A module is a file containing Python definitions and statements.
The file name is the module name with the suffix .py added.
Within a module, the module's name (as a string) is available as the value of the global variable __name__.

This section covers:
- Importing modules
- Executing modules as scripts from the terminal
- Executing modules as scripts from the Python REPL
"""


# =========================================
# 1.1 Importing Modules
# =========================================
"""
There are several ways to import names from a module.

- Import specific names directly: from fibo import fib, fib2
- Import the whole module and use dotted access: import fibo
- Import a name under an alias: from fibo import fib as fibonacci
- Import everything a module exposes: from fibo import *
"""

from fibo import fib, fib2
fib(100)

import fibo
fibo.fib(100)

from fibo import fib as fibonacci
fibonacci(100)

from fibo import *
fib(500)


# =========================================
# 1.2 Executing Modules as Scripts from the Terminal
# =========================================
"""
A module can be run directly as a script from the terminal.

Add code at the end of the fibo module:
if __name__ == "__main__":
    import sys
    fib(int(sys.argv[1]))


Then run it from the terminal:
python fibo.py <arguments>
"""


# =========================================
# 1.3 Executing Modules as Scripts from the Python REPL
# =========================================
"""
A module's functions can also be used interactively from the Python REPL.

from fibo import fib as fibonacci
fibonacci(500)
"""
