# =========================================
# 1. Odds and Ends
# =========================================
"""
This section covers a few useful Python features that do not fit neatly into one category,
but are commonly used in real-world code.

These include:
- Data containers (dataclasses)
- Flexible object usage (duck typing)
- Method object internals
"""


# =========================================
# 1.1 Data Containers with dataclasses
# =========================================
"""
Sometimes you just need a simple object to store data.

In other languages, this might be called:
- a struct (C)
- a record (Pascal)

In Python, the common approach is to use a dataclass.
"""

from dataclasses import dataclass

@dataclass
class Employee:
    name: str
    dept: str
    salary: int


john = Employee('john', 'computer lab', 1000)

print(john.name)   # Outputs: john
print(john.dept)   # Outputs: computer lab
print(john.salary) # Outputs: 1000


"""
dataclass automatically provides:
- __init__()
- __repr__()
- __eq__()

This reduces boilerplate code when storing data.
"""


# =========================================
# 1.2 Flexible Interfaces (Duck Typing)
# =========================================
"""
Python uses "duck typing":

"If it behaves like a given type, it can be used as that type."

This means:
- Objects do not need to share the same class
- They only need to provide the expected methods
"""

def read_first_line(file_like):
    return file_like.readline()

# A real file works
with open(__file__, 'r') as f:
    print(read_first_line(f))


# A custom object can work too
class StringReader:
    def __init__(self, data):
        self.data = data.splitlines()

    def readline(self):
        return self.data[0]

reader = StringReader("hello\nworld")

print(read_first_line(reader))  # Outputs: hello


"""
Key idea:
Python focuses on behaviour, not type.
"""


# =========================================
# 1.3 Method Objects and Their Attributes
# =========================================
"""
Methods are objects in Python, and they have their own attributes.

When you access a method from an instance:
    obj.method

You get a "method object"
"""

class MyClass:
    def greet(self):
        return "hello"

obj = MyClass()

m = obj.greet  # this is a method object

