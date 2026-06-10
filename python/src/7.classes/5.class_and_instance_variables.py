# 1. Class and Instance Variables
"""
Instance variables are for data unique to each instance and class variables 
are for attributes and methods shared by all instances of the class
"""
class Dog:

    kind = 'canine'         # class variable shared by all instances

    def __init__(self, name):
        self.name = name    # instance variable unique to each instance
        self.age = None    # instance variable declared without value
        

# 2. Instance attributes ovverride class attributes
"""
Instance attributes override class attributes during lookup; if both exist, 
the instance value is used instead of the class value.
"""
class Example2:
    value = "class value"

obj = Example2()
obj.value = "instance value"

print(obj.value)   # instance value

# 3.  Class attributes are accessible to methods and external users
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

# 4. Encapsulation relies on conventions (not enforced)
"""Encapsulation in Python relies on conventions rather than enforced access 
restrictions, though lower-level implementations can enforce hiding.
"""
class Example4:
    def __init__(self):
        self._hidden = 42  # convention: "internal/private"

obj = Example4()

# Access is still possible (not truly private)
print(obj._hidden)  # 42

