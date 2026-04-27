# 1.built-in function dir() is used to find out which names a module defines
import fibo, sys
dir(fibo)
'''
['__name__', 'fib', 'fib2']
'''

dir(sys)


# 2. dir() without arguments lists the names of the current local scope
a = [1, 2, 3, 4, 5]
import fibo
fib = fibo.fib
dir()
'''
['__builtins__', '__name__', 'a', 'fib', 'fibo', 'sys']
'''


# 3. builtins lists the names of built-in functions and variables
import builtins
dir(builtins)


