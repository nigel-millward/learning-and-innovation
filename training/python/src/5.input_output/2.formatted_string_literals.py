# =========================================
# 1. Formatted String Literals (f-strings)
# =========================================
"""
Formatted string literals (f-strings) provide a concise way to embed Python expressions
inside strings.

To use them:
- Prefix the string with 'f' or 'F'
- Place expressions inside {}

This allows dynamic construction of strings.
"""


# =========================================
# 1.1 Basic Usage
# =========================================
"""
Expressions inside {} are evaluated and inserted into the string.
"""

name = "Alice"
age = 30

print(f"My name is {name} and I am {age} years old.")
# Outputs: My name is Alice and I am 30 years old


# =========================================
# 1.2 Using Expressions
# =========================================
"""
You can include any valid Python expression inside {}.
"""

x = 10
y = 5

print(f"{x} + {y} = {x + y}")
# Outputs: 10 + 5 = 15


# =========================================
# 1.3 Format Specifiers
# =========================================
"""
You can control formatting using a colon ':' inside {}.

Syntax:
{expression:format_spec}
"""

import math

print(f"The value of pi is approximately {math.pi:.3f}.")
# Outputs: The value of pi is approximately 3.142.


"""
Example:
- .3f → 3 decimal places
"""


# =========================================
# 1.4 Field Width and Alignment
# =========================================
"""
You can control the minimum width of a field.

Values are padded if necessary.
"""

table = {'Sjoerd': 4127, 'Jack': 4098, 'Dcab': 7678}

for name, phone in table.items():
    print(f"{name:10} ==> {phone:10d}")

# Outputs:
# Sjoerd     ==>       4127
# Jack       ==>       4098
# Dcab       ==>       7678


"""
Format details:
- :10   → minimum width of 10 characters
- :10d → integer formatted within width
"""


# =========================================
# 1.5 Conversion Flags (!s, !r, !a)
# =========================================
"""
You can control how values are converted before formatting.

- !s → str()
- !r → repr()
- !a → ascii()
"""

animals = "eels"

print(f"My hovercraft is full of {animals}.")
# Outputs: My hovercraft is full of eels.

print(f"My hovercraft is full of {animals!r}.")
# Outputs: My hovercraft is full of 'eels'


# =========================================
# 1.6 Self-Documenting Expressions (=)
# =========================================
"""
The '=' specifier displays both the expression and its value.

Format:
{expression=}
"""

bugs = "roaches"
count = 13
area = "living room"

print(f"Debugging {bugs=} {count=} {area=}")
# Outputs: Debugging bugs='roaches' count=13 area='living room'


"""
This is especially useful for debugging.
"""


# =========================================
# 1.7 Combining Formatting Features
# =========================================
"""
Multiple formatting options can be combined.
"""

value = 123.456

print(f"{value:10.2f}")  # width 10, 2 decimal places
# Outputs: '    123.46'


# =========================================
# 1.8 Key Idea
# =========================================
"""
f-strings allow you to:

- Embed expressions directly in strings
- Control formatting inline
- Produce clean, readable output

They are the preferred string formatting method in modern Python.
"""


# =========================================
# 1.9 Summary
# =========================================
"""
Formatted string literals provide:

- Simple syntax: f"... {expression} ..."
- Powerful formatting with ':'
- Conversion control with !s, !r, !a
- Debugging support with '='

Best practices:
- Use f-strings for most string formatting
- Use format specifiers for alignment and precision
- Use '=' when debugging

Core idea:
"Embed logic directly into readable string output"
"""
