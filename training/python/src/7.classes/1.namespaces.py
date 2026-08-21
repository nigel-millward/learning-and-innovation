# =========================================
# 1. Namespaces
# =========================================
"""
A Python namespace is a system that ensures all the names in a program are unique
and can be used without any conflict. Under the hood, Python implements namespaces as
standard dictionaries, mapping variable, function, and class names (as keys) to their
corresponding memory objects (as values).

This module covers:
- What a namespace is
- The types of namespaces
- A code example of namespaces
- Checking namespaces directly
- How namespaces relate to module objects
"""


# =========================================
# 1.1 Namespace overview
# =========================================
"""A Python namespace is a system that ensures all the names in a program are unique
and can be used without any conflict. Under the hood, Python implements namespaces as
standard dictionaries, mapping variable, function, and class names (as keys) to their
corresponding memory objects (as values)
"""


# =========================================
# 1.2 Types of namespaces
# =========================================
"""
Python has 4 main namespaces:

Built-in: Contains all of Python’s core built-in functions (like print() or len())
and standard exceptions. It is created when the Python interpreter starts up and r
emains until it shuts down.

Global: Holds names defined at the top level of a module or file, including imported
packages. It is created when the module is read and lasts until the script execution ends.

Enclosing: Created when a function is defined inside another function.It contains names
defined in the outer (enclosing) function, making them accessible to the inner function.

Local: Created dynamically whenever a function is called. It holds arguments and variables
declared inside that specific function and is discarded as soon as the function returns

"""


# =========================================
# 1.3 Code example of namespaces
# =========================================

# This 'x' lives in the Global Namespace
x = "I am Global"

def outer_function():
    # This 'x' lives in the Enclosing Namespace
    x = "I am Enclosing"

    def inner_function():
        # This 'x' lives in the Local Namespace
        x = "I am Local"
        print(x) # Python finds Local first

    inner_function()

outer_function()
print(x) # Python finds Global here

"""
Output:
I am Local
I am Global
"""


# =========================================
# 1.4 Checking namespaces directly
# =========================================
globals() # returns a dictionary of the current global namespace
locals() # returns a dictionary of the current local namespace


# =========================================
# 1.5 Namespaces explained
# =========================================
"""
Example, src/pandas/test.py & inside test.py:
"""
x = 10

class Example:
    pass

def myfunction():
    pass
"""
when pandas.test is imported, python creates a module object pandas.test.
This is an object of type 'module'.

Inside that module object, is a namespace (a dictionary):  pandas.test.__dict__
Conceptually:
{
    "x": 10,
    "Example": <class pandas.test.Example>,
    "myfunction": <function pandas.test.myfunction>,
    "__name__": "pandas.test",
    ...
}

The module is an object
The namespace is the dictionary of attributes inside that module object
"""
