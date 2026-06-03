# 1. Instance objects
"""An instance object is a concrete item created from a class template. 
You can only do two things with it: use its data or call its actions.
"""

# 2. Data attributes - instance variables
"""
These are variables attached directly to a specific object. 
They store information and do not need to be created in advance; 
they appear the moment you assign a value to them
"""


class MyClass:
    pass  # An empty class template

x = MyClass()  # Create an instance object

# 1. Create a data attribute on the fly
x.counter = 1

# 2. Use it in a loop
while x.counter < 10:
    x.counter = x.counter * 2

# 3. Print the result (Prints 16)
print(x.counter)

# 4. Delete the attribute entirely
del x.counter



# 3. Methods (Object actions)
"""
Methods are functions attached to an object. If a class has a function inside it, 
every instance of that class gets a corresponding method to use
"""

class MyClass:
    i = 12345  # This is a class variable, not a function

    def f(self):  # This function defines a method for instances
        return "hello world"


x = MyClass()  # Create an instance object

# x.f is valid because MyClass.f is a function
print(x.f())  # Prints "hello world"

