# 1. The built-in function float() can be used for converting text strings
# and numbers to float objects. Consider the following example

float(3.8)

# 2.Running help(float)
help(float)

"""
class float(object)
 float(x=0, /)
 Convert a string or number to a floating point number, if possible.
"""


# 3.It turns out that while the one parameter of float() is called x,
# you’re not allowed to use its name:

"""
>>> float(x="3.8")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: float() takes no keyword arguments
"""

# When using float() you’re only allowed to specify arguments by position, not by keyword. Before Python 3.8,
# such positional-only arguments were only possible for built-in functions. There was no easy way to specify
# that arguments should be positional-only in your own functions


#4. Pre 3.8, you could not enforce positional arguments in your own custom methods.
# you could type keyword and position

#3.7
def incr(x):
    return x + 1

incr(3.8)
incr(x=3.8)

#5. In Python 3.8, you can use / to denote that all arguments before it must be specified by position.
# You can rewrite incr() to only accept positional arguments:
def incr(x, /):
    return x + 1

incr(3.8)

incr(x=3.8)
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# TypeError: incr() got some positional-only arguments passed as
#            keyword arguments: 'x'



