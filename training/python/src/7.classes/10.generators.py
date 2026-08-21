# =========================================
# 1. Generators: The Basics
# =========================================
"""
Generators are a simple and powerful way to create iterators.

They look like normal functions, but instead of returning values,
they use the 'yield' keyword.

Each time next() is called:
- The function resumes where it left off
- It remembers its state automatically
"""


# =========================================
# 1.1 A Simple Generator Example
# =========================================
"""
This generator yields characters in reverse order.
"""

def reverse(data):
    for index in range(len(data) - 1, -1, -1):
        yield data[index]


for char in reverse("golf"):
    print(char)

# Outputs:
# f
# l
# o
# g


# =========================================
# 1.2 How Generators Work
# =========================================
"""
Calling a generator function does not run it immediately.

Instead, it returns a generator object.
"""

gen = reverse("abc")

print(gen)  # Outputs: <generator object ...>

print(next(gen))  # c (from end → c)
print(next(gen))  # b
print(next(gen))  # a

# next(gen) would raise StopIteration


# =========================================
# 1.3 Execution Pausing and Resuming
# =========================================
"""
Each 'yield' pauses the function and saves:
- Local variables
- Current position in code

When next() is called:
- Execution resumes from the last yield
"""

def counter():
    print("Start")
    yield 1
    print("Middle")
    yield 2
    print("End")

c = counter()

print(next(c))  # Start → 1
print(next(c))  # Middle → 2
# next(c) → StopIteration after printing "End"


# =========================================
# 1.4 Generators vs Class-Based Iterators
# =========================================
"""
Anything you can do with a class-based iterator,
you can also do with a generator.

Generators automatically provide:
- __iter__()
- __next__()
"""

# Class-based iterator (from previous module)
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


# Equivalent generator version
def counter_gen(limit):
    current = 0
    while current < limit:
        yield current
        current += 1


print(list(counter_gen(3)))  # Outputs: [0, 1, 2]


"""
The generator version:
- Is shorter
- Easier to read
- Requires less boilerplate
"""


# =========================================
# 1.5 Automatic State Management
# =========================================
"""
Generators automatically handle:
- Saving execution state
- Managing variables between calls
- Raising StopIteration when done

This removes the need for:
- self variables
- manual state tracking
"""


# =========================================
# 1.6 StopIteration in Generators
# =========================================
"""
When a generator finishes execution, it automatically raises StopIteration.

You do not need to raise it manually.
"""

def simple():
    yield 1
    yield 2

s = simple()

print(next(s))  # 1
print(next(s))  # 2
# next(s) → StopIteration


# =========================================
# 1.7 Key Idea
# =========================================
"""
A generator is:
- A function that produces a sequence of values over time
- A simpler way to implement iterators

Key feature:
Execution pauses at 'yield' and resumes on demand
"""


# =========================================
# 1.8 Summary
# =========================================
"""
Generators provide:

- Simple iterator creation using 'yield'
- Automatic state management
- Built-in StopIteration handling

They are often preferred over class-based iterators because:
- Less code
- Clearer logic
- Easier to maintain
"""