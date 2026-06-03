# 1. class syntax
"""
A Python class definition must run before it can be used, similar to how functions work. 
When Python enters a class definition, it creates a temporary workspace (or namespace) 
where everything inside that class—like variables and functions—is stored. While classes 
usually contain functions, they can also hold other types of code. Once Python finishes 
reading the class definition, it packages that workspace into a final "class object" 
and links it to the class name so you can use it later in your program.
"""

class ClassName:
    # class body
    pass

# 2. class objects
"""
A Python class object is a blueprint that does two things: 
- you can look up its data and functions (attribute references)
- or you can use it to build new items (instantiation)
"""


#2.1 attribute references
"""
You can access or change data directly on the blueprint using a dot (.)
"""
class MyClass:
    """A simple example class"""
    i = 12345  # A class variable
    
    def f(self):
        return 'hello world'

# Read attributes directly from the blueprint
print(MyClass.i)      # Outputs: 12345
print(MyClass.__doc__) # Outputs: "A simple example class"

# You can modify them too
MyClass.i = 99999
print(MyClass.i)      # Outputs: 99999


# 2.2  Class instantiation - making new objects
"""
To create a real object from the blueprint, call the class like a function. 
This creates a unique instance of the class.
"""

# Create a new instance named 'x'
x = MyClass()

# 'x' can now run the function defined in the class
print(x.f())  # Outputs: 'hello world'


# 2.3 Customizing New Objects  with init
"""
The __init__ method automatically runs the moment you create a new object. It sets up the starting data for that specific instance
You can pass data into the class when creating it to make each object unique from the start
"""

class Dog:
    def __init__(self):
        self.status = "happy" # Every new dog starts happy

my_dog = Dog()
print(my_dog.status)  # Outputs: happy

class ComplexNumber:
    def __init__(self, realpart, imagpart):
        self.r = realpart  # Assigns the input to this specific object
        self.i = imagpart

# Create a unique number object
x = ComplexNumber(3.0, -4.5)

# Read the object's unique data
print(x.r)  # Outputs: 3.0
print(x.i)  # Outputs: -4.5
