# =========================================
# 1. break and continue
# =========================================
"""
This section covers two statements that change the normal flow of a loop.

It includes:
- break, which exits the loop early
- continue, which skips to the next iteration
"""


# =========================================
# 1.1 The break Statement
# =========================================
"""
break exits the innermost enclosing for or while loop.

In the example below, the inner loop stops as soon as a divisor is found.
"""

# break exits the innermost enclosing for or while loop & for loop
for n in range(2, 10):
    for x in range(2, n):
        if n % x == 0:
            print(f'{n} equals {x} * {n//x}')
            break
"""
4 equals 2 * 2
6 equals 2 * 3
8 equals 2 * 4
9 equals 3 * 3
"""


# =========================================
# 1.2 The continue Statement
# =========================================
"""
continue skips the rest of the current loop body, but continues with the next
iteration.
"""

# continue skips the rest of the current loop, but continues with the next iteration
for num in range(2, 10):
    if num % 2 == 0:
        print(f'{num} is an even number')
        continue
    print(f'{num} is an odd number')
"""
2 is an even number
3 is an odd number
4 is an even number
5 is an odd number
6 is an even number
7 is an odd number
8 is an even number
9 is an odd number
"""

