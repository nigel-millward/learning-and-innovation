# =========================================
# 1. for Loops
# =========================================
"""
This section covers the for loop, which iterates over the items of any sequence
(such as a list or a string) in order.

It includes:
- Iterating over a list
- Strategies for modifying a collection while iterating
- Iterating over a number range
"""


# =========================================
# 1.1 Measure Some Strings
# =========================================
"""
A for loop iterates over the items of a sequence in the order they appear.

Here we loop over a list of words and print each word alongside its length.
"""

# 1. Measure some strings
words = ['cat', 'window', 'defenestrate']
for w in words:
    print(w, len(w))

"""
cat 3
window 6
defenestrate 12
"""


# =========================================
# 1.2 Modifying a Collection While Iterating
# =========================================
"""
You should not modify a collection while iterating directly over it.

Two safe strategies are:
- Iterate over a copy of the collection
- Build a new collection instead of changing the original
"""

# 2.1 create a sample collection
users = {
    'Hans': 'active',
    'Greta': 'inactive',
    'Fritz': 'active'
}

# 2.2 Strategy: Iterate over a copy
for user, status in users.copy().items():
    if status == 'inactive':
        del users[user]

# 2.3 Strategy: create a new collection
active_users = {}
for user, status in users.items():
    if status == 'active':
        active_users[user] = status


# =========================================
# 1.3 Iterating Over a Number Range
# =========================================
"""
To repeat an action a fixed number of times, loop over a range of numbers.

range(5) produces the numbers 0 through 4.
"""

# 2.4 Strategy: iterate over number range
for i in range(5):
    print(i)


