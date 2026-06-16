# =========================================
# 1. match Statements
# =========================================
"""
The match statement allows you to match a value against a series of patterns
given as one or more case blocks. This is superficially similar to a switch
statement in Java.

This section includes:
- Comparing a subject value to literal values
- Using an if clause to add a guard to a pattern
- Using named constants in patterns
"""


# =========================================
# 1.1 Comparing a Subject to Literal Values
# =========================================
"""
The simplest match compares the subject value to literal values.

A single case can match several literals using the | operator, and the wildcard
pattern _ matches anything that was not matched earlier.
"""

# Example 1: compare subject value to literal values
def http_error(status):
    match status:
        case 400:
            return "Bad request"
        case 401 | 403:
            return "Not allowed"
        case 404:
            return "Not found"
        case 418:
            return "I'm a teapot"
        case _:
            return "Something's wrong with the internet"



# =========================================
# 1.2 Adding a Guard with an if Clause
# =========================================
"""
Using the if clause to add a guard to a pattern.

The pattern only matches when the guard condition is also true.
"""

# Example 3: Uisng the if clause to add a guard to a pattern
def greet(name):
    match name:
        case "Alice" | "Bob" if len(name) < 5:
            return f"Hello, {name}!"
        case _:
            return "Hello, stranger!"


# =========================================
# 1.3 Using Named Constants in Patterns
# =========================================
"""
Patterns may use named constants. These must be dotted names to prevent them
from being interpreted as capture variables.
"""

# Example 3: Patterns may use named constants.
# These must be dotted names to prevent them from being interpreted as capture variables:
from enum import Enum
class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'

color = Color(input("Enter your choice of 'red', 'blue' or 'green': "))

match color:
    case Color.RED:
        print("I see red!")
    case Color.GREEN:
        print("Grass is green")
    case Color.BLUE:
        print("I'm feeling the blues :(")
