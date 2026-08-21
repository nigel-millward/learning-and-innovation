# =========================================
# 1. Class and Instance Variables
# =========================================
"""
Instance variables are for data unique to each instance and class variables
are for attributes and methods shared by all instances of the class.

This module covers:
- Class and instance variables
- Instance attributes overriding class attributes
- Class attributes being accessible to methods and external users
- Encapsulation by convention (not enforced)
- How direct modification can break invariants
- Adding new attributes dynamically
- Why explicit self improves readability
- self as a naming convention
- Functions assigned to class attributes becoming methods
- Methods calling other methods via self
- Methods accessing global names
- Every value being an object with a class
"""


# =========================================
# 1.1 Class and Instance Variables
# =========================================
"""
Instance variables are for data unique to each instance and class variables
are for attributes and methods shared by all instances of the class
"""
class Dog:

    kind = 'canine'         # class variable shared by all instances

    def __init__(self, name):
        self.name = name    # instance variable unique to each instance
        self.age = None    # instance variable declared without value


# =========================================
# 1.2 Instance attributes override class attributes
# =========================================
"""
Instance attributes override class attributes during lookup; if both exist,
the instance value is used instead of the class value.
"""
class Example2:
    value = "class value"

obj = Example2()
obj.value = "instance value"

print(obj.value)   # instance value


# =========================================
# 1.3 Class attributes are accessible to methods and external users
# =========================================
"""
Class data attributes are accessible to both methods and external users,
so Python does not enforce strict data hiding.
"""
class Example3:
    value = 10

    def show(self):
        return self.value

obj = Example3()
print(obj.value)     # 10 (external access)
print(obj.show())    # 10 (method access)


# =========================================
# 1.4 Encapsulation relies on conventions (not enforced)
# =========================================
"""Encapsulation in Python relies on conventions rather than enforced access
restrictions, though lower-level implementations can enforce hiding.
"""
class Example4:
    def __init__(self):
        self._hidden = 42  # convention: "internal/private"

obj = Example4()

# Access is still possible (not truly private)
print(obj._hidden)  # 42


# =========================================
# 1.5 Direct modification can break invariants
# =========================================
"""Modifying data attributes directly can break invariants maintained by methods,
so clients should handle them carefully.
"""
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

c = Counter()
c.value = -100  # breaks expected logic
print(c.value)


# =========================================
# 1.6 Users can add new attributes dynamically
# =========================================
"""Users can add new attributes to instances without breaking methods, provided naming conflicts are avoided."""
class Example:
    def greet(self):
        return "Hello"

obj = Example()
obj.new_attr = 123  # added dynamically
print(obj.new_attr)


# =========================================
# 1.7 Explicit self improves readability
# =========================================
"""Explicit attribute references (e.g., self.x) improve readability by clearly distinguishing instance variables
from local variables."""
class Example:
    def __init__(self):
        self.value = 5

    def show(self):
        value = 10
        return self.value, value  # no confusion


# =========================================
# 1.8 self is just a naming convention
# =========================================
"""The name self is a convention for the first method parameter; it has no special meaning but
improves readability and tooling compatibility."""
class Example:
    def show(this):
        return "Works fine"

obj = Example()
print(obj.show())
# output: Works fine


# =========================================
# 1.9 Functions assigned to class attributes become methods
# =========================================
"""Any function assigned as a class attribute becomes a method, even if defined outside the class;
however, this can reduce code clarity."""

def external_func(self):
    return "Hello"

class Example:
    greet = external_func

obj = Example()
print(obj.greet())


# =========================================
# 1.10 Methods can call other methods via self
# =========================================
"""Methods can call other methods via self, enabling reuse of logic within the same class."""
class Example:
    def hello(self):
        return "Hello"

    def greet(self):
        return self.hello() + " World"

obj = Example()
print(obj.greet())


# =========================================
# 1.11 Methods can access global names
# =========================================
"""Methods can access global names from their defining module, though heavy reliance on
global data is generally discouraged."""
x = 10

class Example:
    def get_x(self):
        return x  # global variable

print(Example().get_x())


# =========================================
# 1.12 Every value is an object with a class
# =========================================
"""Every value in Python is an object with an associated class/type, accessible via object.__class__."""
x = 5
print(type(x))          # <class 'int'>
print(x.__class__)      # <class 'int'>
