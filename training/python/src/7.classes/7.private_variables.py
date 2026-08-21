# =========================================
# 1. Private Variables (Python Style)
# =========================================
"""
Python does not enforce true private variables.

Instead, it follows a naming convention:
- A single leading underscore (e.g. _value) means "internal use"
- It signals that something is not part of the public API

This is a convention, not a restriction.
"""


# =========================================
# 1.1 Non-Public Variables (Single Underscore)
# =========================================
"""
A name starting with a single underscore should be treated as internal.

It:
- Should not be accessed outside the class
- May change without notice
- Is still technically accessible
"""

class MyClass:
    def __init__(self):
        self._internal_value = 42  # intended for internal use

obj = MyClass()

# Accessible, but discouraged
print(obj._internal_value)  # Outputs: 42


# =========================================
# 1.2 Name Mangling (Double Underscore)
# =========================================
"""
Python provides limited support for "private" variables using name mangling.

Any variable with:
- At least two leading underscores
- At most one trailing underscore

Is automatically renamed by Python to avoid name conflicts.

Format:
__name  →  _ClassName__name
"""

class MyClass:
    def __init__(self):
        self.__hidden = "secret"

obj = MyClass()

# Direct access fails
# print(obj.__hidden)  # AttributeError

# Access using the mangled name
print(obj._MyClass__hidden)  # Outputs: secret


# =========================================
# 1.3 Why Name Mangling Exists
# =========================================
"""
Name mangling is used to:
- Prevent accidental name clashes in subclasses
- Protect internal implementation details

It is NOT designed for strict security
"""


# =========================================
# 1.4 Name Mangling with Inheritance
# =========================================
"""
Each class mangles names independently.

This allows subclasses to define their own variables
without interfering with parent class internals.
"""

class Base:
    def __init__(self):
        self.__value = "base"

class Child(Base):
    def __init__(self):
        super().__init__()
        self.__value = "child"

c = Child()

# Two separate variables exist
print(c._Base__value)   # Outputs: base
print(c._Child__value)  # Outputs: child


# =========================================
# 1.5 Practical Example: Avoiding Method Conflicts
# =========================================
"""
Name mangling helps prevent subclasses from accidentally breaking internal logic.
"""

class Mapping:
    def __init__(self, iterable):
        self.items_list = []
        self.__update(iterable)  # calls internal version

    def update(self, iterable):
        for item in iterable:
            self.items_list.append(item)

    __update = update  # private copy

class MappingSubclass(Mapping):
    def update(self, keys, values):
        # New method with different behaviour
        for item in zip(keys, values):
            self.items_list.append(item)

m = MappingSubclass([1, 2, 3])

# __init__ still works correctly
print(m.items_list)  # Outputs: [1, 2, 3]


# =========================================
# 1.6 Important Notes
# =========================================
"""
- Name mangling is meant to avoid accidents, not enforce privacy
- You can still access mangled names if needed
- Useful for:
    - Debugging
    - Advanced use cases

Some limitations:
- exec() and eval() do not apply name mangling
- getattr(), setattr(), and direct __dict__ access bypass it
"""


# =========================================
# 1.7 Summary
# =========================================
"""
Python uses conventions rather than strict access control:

- _name → internal use (convention only)
- __name → name mangling (avoids clashes)

Key idea:
"Private" in Python means "should not be used", not "cannot be used"
"""