# =========================================
# 1. if Statements
# =========================================
"""
This section covers the if statement, Python's primary tool for conditional execution.

It includes:
- Branching with if / elif / else
- Membership testing with the in keyword
"""


# =========================================
# 1.1 Branching with if / elif
# =========================================
"""
An if statement runs a block of code only when its condition is true.

You can chain conditions:
- if    tests the first condition
- elif  tests further conditions if earlier ones were false
- else  (optional) runs when none of the conditions matched

Only the first matching branch runs.
"""

x = int(input("Please enter an integer: "))
if x < 0:
    x = 0
    print('Negative changed to zero')
elif x == 0:
    print('Zero')
elif x == 1:
    print('Single')
elif x > 1:
    print('More than 1')


# =========================================
# 1.2 Membership Testing with the in Keyword
# =========================================
"""
The in keyword checks whether a value is a member of a collection.

This is a clean way to test a value against several accepted options without
writing many separate comparisons.
"""

# in keyword
reply = input("Do you want to continue? (y/n): ").lower()
if reply in {'y', 'ye', 'yes'}:
    pass
