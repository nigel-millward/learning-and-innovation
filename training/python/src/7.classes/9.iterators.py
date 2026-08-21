# =========================================
# 1. Iterators: The Basics
# =========================================
"""
An iterator is an object that allows you to loop over a sequence of data one item at a time.

Many Python objects are iterable, meaning they can be used in a for-loop:
- lists
- tuples
- dictionaries
- strings
- files

This consistent behaviour makes iteration simple and uniform across Python.
"""


# =========================================
# 1.1 Iterating Over Common Objects
# =========================================
"""
Most container types can be looped over using a for statement.
"""

for element in [1, 2, 3]:
    print(element)

for element in (1, 2, 3):
    print(element)

for key in {'one': 1, 'two': 2}:
    print(key)

for char in "123":
    print(char)


# Example with files
# for line in open("myfile.txt"):
#     print(line, end='')


"""
The for loop works the same way for all of these types.
This is made possible by the iterator protocol.
"""


# =========================================
# 1.2 The Iterator Protocol
# =========================================
"""
Behind the scenes, a for loop does the following:

1. Calls iter(obj) to get an iterator
2. Repeatedly calls next() to get values
3. Stops when StopIteration is raised
"""

s = "abc"

it = iter(s)  # get iterator

print(it)  # Outputs: <str_iterator object ...>

print(next(it))  # Outputs: a
print(next(it))  # Outputs: b
print(next(it))  # Outputs: c

# next(it) would raise StopIteration


# =========================================
# 1.3 StopIteration
# =========================================
"""
When there are no more items, the iterator raises StopIteration.

The for loop automatically handles this and exits cleanly.
"""

it = iter([1])

print(next(it))  # Outputs: 1

# print(next(it))  # Raises StopIteration


# =========================================
# 1.4 Creating Your Own Iterator
# =========================================
"""
To make a class iterable, implement:

- __iter__() → returns an iterator object
- __next__() → returns the next item
"""

class Counter:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration

        value = self.current
        self.current += 1
        return value


c = Counter(3)

for num in c:
    print(num)

# Outputs:
# 0
# 1
# 2


# =========================================
# 1.5 Example: Reverse Iterator
# =========================================
"""
This iterator walks through a sequence in reverse.
"""

class Reverse:
    """Iterator for looping over a sequence backwards."""
    
    def __init__(self, data):
        self.data = data
        self.index = len(data)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == 0:
            raise StopIteration

        self.index -= 1
        return self.data[self.index]


rev = Reverse("spam")

print(iter(rev))  # Iterator object

for char in rev:
    print(char)

# Outputs:
# m
# a
# p
# s


# =========================================
# 1.6 Key Idea
# =========================================
"""
An iterable is any object that can produce an iterator.

An iterator:
- keeps track of position
- returns one item at a time
- raises StopIteration when finished
"""


# =========================================
# 1.7 Summary
# =========================================
"""
Iteration in Python is based on a simple protocol:

- iter(obj) → gets an iterator
- next(iterator) → gets next value
- StopIteration → signals the end

This design:
- keeps loops simple
- works across many data types
- allows custom iteration logic
"""