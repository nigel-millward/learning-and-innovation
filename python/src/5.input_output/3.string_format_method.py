# =========================================
# 1. The str.format() Method
# =========================================
"""
The str.format() method allows you to insert values into a string
using placeholders marked by {}.

These placeholders are replaced by values passed to .format().
"""


# =========================================
# 1.1 Basic Usage
# =========================================
"""
Place {} in the string and provide values in .format().
"""

print("We are the {} who say '{}'!".format("knights", "Ni"))

# Outputs: We are the knights who say "Ni!"


# =========================================
# 1.2 Positional Arguments
# =========================================
"""
You can reference values by their position using numbers inside {}.
"""

print("{0} and {1}".format("spam", "eggs"))
# Outputs: spam and eggs

print("{1} and {0}".format("spam", "eggs"))
# Outputs: eggs and spam


# =========================================
# 1.3 Keyword Arguments
# =========================================
"""
You can name arguments and refer to them using their names.
"""

print("This {food} is {adjective}.".format(
    food="spam",
    adjective="absolutely horrible"
))

# Outputs: This spam is absolutely horrible.


# =========================================
# 1.4 Mixing Positional and Keyword Arguments
# =========================================
"""
You can combine positional and keyword arguments.
"""

print("The story of {0}, {1}, and {other}.".format(
    "Bill",
    "Manfred",
    other="Georg"
))

# Outputs: The story of Bill, Manfred, and Georg.


# =========================================
# 1.5 Accessing Data Structures
# =========================================
"""
You can access elements inside containers directly in {}.
"""

table = {"Sjoerd": 4127, "Jack": 4098, "Dcab": 8637678}

print("Jack: {0[Jack]:d}; Sjoerd: {0[Sjoerd]:d}; "
      "Dcab: {0[Dcab]:d}".format(table))

# Outputs:
# Jack: 4098; Sjoerd: 4127; Dcab: 8637678


# =========================================
# 1.6 Using ** with Dictionaries
# =========================================
"""
You can unpack dictionaries using ** to pass values as keywords.
"""

table = {"Sjoerd": 4127, "Jack": 4098, "Dcab": 8637678}

print("Jack: {Jack:d}; Sjoerd: {Sjoerd:d}; Dcab: {Dcab:d}".format(**table))

# Outputs:
# Jack: 4098; Sjoerd: 4127; Dcab: 8637678


# =========================================
# 1.7 Using vars()
# =========================================
"""
The vars() function returns a dictionary of local variables.

This can be used with .format().
"""

name = "Python"
version = 3.11

values = vars()

print("Name: {name}, Version: {version}".format(**values))

# Outputs: Name: Python, Version: 3.11


# =========================================
# 1.8 Formatting Numbers and Alignment
# =========================================
"""
You can control width, alignment, and formatting using ':'.

Syntax:
{value:format_spec}
"""

for x in range(1, 6):
    print("{0:2d} {1:3d} {2:4d}".format(x, x*x, x*x*x))

# Outputs:
#  1   1    1
#  2   4    8
#  3   9   27
#  4  16   64
#  5  25  125


"""
Format details:
- 2d → width 2 integer
- 3d → width 3 integer
- 4d → width 4 integer
"""


# =========================================
# 1.9 Key Idea
# =========================================
"""
The str.format() method allows:

- Flexible placement of values
- Access to complex data structures
- Detailed control over formatting

It is more verbose than f-strings but more explicit.
"""


# =========================================
# 1.10 Summary
# =========================================
"""
str.format() provides:

- Positional formatting: {0}, {1}
- Keyword formatting: {name}
- Data access: {0[key]}
- Formatting control with ':'

Best practices:
- Use f-strings for simple cases
- Use .format() for complex or structured formatting
- Use dictionary unpacking for dynamic data

Core idea:
"Insert and format values using flexible placeholders"
"""