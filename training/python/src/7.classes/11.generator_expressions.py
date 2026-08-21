# =========================================
# 1. Generator Expressions
# =========================================
"""
Generator expressions provide a compact way to create generators.

They are similar to list comprehensions, but:
- Use parentheses () instead of square brackets []
- Produce values one at a time (lazy evaluation)
- Are more memory efficient

They are best used when the result is needed immediately.
"""


# =========================================
# 1.1 Basic Syntax
# =========================================
"""
Generator expression syntax:

(expression for item in iterable)

This creates a generator without defining a full function.
"""

gen = (x * x for x in range(5))

print(gen)  # Outputs: <generator object ...>

print(list(gen))  # Outputs: [0, 1, 4, 9, 16]


# =========================================
# 1.2 Immediate Use with Functions
# =========================================
"""
Generator expressions are often passed directly into functions.

This avoids creating intermediate data structures.
"""

# Sum of squares
result = sum(i * i for i in range(10))

print(result)  # Outputs: 285


# =========================================
# 1.3 Working with Multiple Variables
# =========================================
"""
You can use multiple variables in generator expressions.
"""

xvec = [10, 20, 30]
yvec = [7, 5, 3]

# Dot product
result = sum(x * y for x, y in zip(xvec, yvec))

print(result)  # Outputs: 260


# =========================================
# 1.4 Nested Iteration
# =========================================
"""
Generator expressions can include multiple loops.
"""

page = ["hello world", "python code"]

unique_words = set(
    word
    for line in page
    for word in line.split()
)

print(unique_words)  # Outputs: {'hello', 'world', 'python', 'code'}


# =========================================
# 1.5 Using with Built-in Functions
# =========================================
"""
Generator expressions work well with functions like:
- sum()
- max()
- min()
- any()
- all()
"""

class Student:
    def __init__(self, name, gpa):
        self.name = name
        self.gpa = gpa

graduates = [
    Student("Alice", 3.9),
    Student("Bob", 3.7),
    Student("Charlie", 4.0),
]

# Find highest GPA
valedictorian = max(
    (student.gpa, student.name) for student in graduates
)

print(valedictorian)  # Outputs: (4.0, 'Charlie')


# =========================================
# 1.6 Comparing to List Comprehensions
# =========================================
"""
List comprehension:
- Creates the full list in memory

Generator expression:
- Produces items one at a time

Example:
"""

data = "golf"

# Generator expression
gen = (data[i] for i in range(len(data) - 1, -1, -1))
print(list(gen))  # Outputs: ['f', 'l', 'o', 'g']

# Equivalent list comprehension
lst = [data[i] for i in range(len(data) - 1, -1, -1)]
print(lst)  # Outputs: ['f', 'l', 'o', 'g']


"""
Key difference:
- list → stored in memory immediately
- generator → computed on demand
"""


# =========================================
# 1.7 Key Idea
# =========================================
"""
Generator expressions are best when:
- You only need to iterate once
- You are passing data into another function
- You want to save memory

They trade flexibility for simplicity and efficiency.
"""


# =========================================
# 1.8 Summary
# =========================================
"""
Generator expressions provide:

- A compact way to create generators
- Lazy evaluation (compute values as needed)
- Memory efficiency compared to lists

Syntax reminder:
(expression for item in iterable)

Key idea:
"Generate values on demand, instead of storing them all at once"
"""