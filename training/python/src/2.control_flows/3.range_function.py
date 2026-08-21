# =========================================
# 1. The range() Function
# =========================================
"""
This section covers the built-in range() function, which generates arithmetic
progressions and is commonly used to drive for loops.

It includes:
- range(stop)
- range(start, stop)
- range(start, stop, step)
- Iterating over the indices of a sequence
- Passing range() to functions that take iterables
"""


# =========================================
# 1.1 range(stop)
# =========================================
"""
If you need to iterate over a sequence of numbers, the built-in function range()
generates arithmetic progressions.

range(n) can be used to specify a number of iterations, producing the numbers
from 0 up to (but not including) n.
"""

# range(n) can be used to specify iterations
for i in range(5):
    print(i)
"""
0, 1, 2, 3, 4
"""


# =========================================
# 1.2 range(start, stop)
# =========================================
"""
range(n, n) can also be used to specify a start and stop value.

The sequence begins at the start value and ends just before the stop value.
"""

# range(n, n) can also be used to specify a start and stop value
for i in range(5, 10):
    print(i)
"""
5, 6, 7, 8, 9
"""


# =========================================
# 1.3 range(start, stop, step)
# =========================================
"""
range(n, n, n) can also specify start, stop and step.

The step controls the increment between successive values.
"""

# range(n, n, n) can also specify start, stop and step
for i in range(0, 10, 3):
    print(i)
"""
0, 3, 6, 9
"""


# =========================================
# 1.4 Iterating Over the Indices of a Sequence
# =========================================
"""
Combining range() with len() lets you iterate over the indices of a sequence,
giving access to both the position and the item at that position.
"""

# iterate over a indices of a sequence
a = ['Mary', 'had', 'a', 'little', 'lamb']
for i in range(len(a)):
    print(i, a[i])
"""
0 Mary
1 had
2 a
3 little
4 lamb
"""


# =========================================
# 1.5 Passing range() to Functions
# =========================================
"""
Functions can take iterables as arguments, so you can use range() to generate a
sequence of numbers to iterate over.
"""

# functions can take iterables as arguments, so can use range() to generate a sequence of numbers to iterate over
sum(range(4))  # 0 + 1 + 2 + 3 = 6


