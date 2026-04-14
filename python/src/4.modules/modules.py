# modules
'''
A module is a file containing Python definitions and statements. 
The file name is the module name with the suffix .py added. 
Within a module, the module’s name (as a string) is available as the value of the global variable __name__.
'''


# 1. import modules
from fibo import fib, fib2
fib(100)

import fibo
fibo.fib(100)

from fibo import fib as fibonacci
fibonacci(100)

from fibo import *
fib(500)

# 2. executing modules as scripts from terminal
'''
Add code at the end of fibo module:
if __name__ == "__main__":
    import sys
    fib(int(sys.argv[1]))


python fibo.py <arguments>
'''

# executing modules as scripts python repl
'''
from fibo import fib as fibonacci
fibonacci(500)
'''



