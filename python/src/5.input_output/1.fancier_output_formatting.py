# =========================================
# 1. Fancier Output Formatting
# =========================================
"""
Python provides several ways to control how output is formatted.

Instead of simple printing, you can:
- Insert values into strings
- Control spacing and alignment
- Format numbers and percentages
- Create readable or debugging-friendly output
"""


# =========================================
# 1.1 Formatted String Literals (f-strings)
# =========================================
"""
F-strings are the most modern and convenient way to format strings.

Prefix a string with 'f' and insert expressions inside {}.
"""

year = 2016
event = "Referendum"

result = f"Results of the {year} {event}"

print(result)  # Outputs: Results of the 2016 Referendum


"""
You can include any valid Python expression inside {}.
"""


# =========================================
# 1.2 Formatting Numbers in f-strings
# =========================================
"""
F-strings support formatting options inside {} using a colon.
"""

value = 3.14159

print(f"{value:.2f}")   # Outputs: 3.14 (2 decimal places)
print(f"{value:10.2f}") # Outputs: '      3.14' (width + alignment)


# =========================================
# 1.3 Using str.format()
# =========================================
"""
The str.format() method provides more explicit formatting control.

Place {} in the string and pass values into .format().
"""

yes_votes = 42_572_654
total_votes = 85_705_149

percentage = yes_votes / total_votes

result = "{:-9} YES votes  {:2.2%}".format(yes_votes, percentage)

print(result)
# Outputs:  42572654 YES votes  49.67%


"""
Formatting options:
- Width (padding)
- Alignment
- Number formatting (percentages, decimals)
"""


# =========================================
# 1.4 Manual String Construction
# =========================================
"""
You can also build strings manually using concatenation and methods.
"""

x = 10 * 3.25
y = 200 * 200

s = "The value of x is " + str(x) + ", and y is " + str(y) + "..."

print(s)
# Outputs: The value of x is 32.5, and y is 40000...


"""
String methods like ljust(), rjust(), and center() can help with layout.
"""

name = "Python"

print(name.ljust(10))   # Left-aligned
print(name.rjust(10))   # Right-aligned
print(name.center(10))  # Centered


# =========================================
# 1.5 str() vs repr()
# =========================================
"""
str() and repr() convert values to strings.

- str() → user-friendly output
- repr() → developer/debugging output
"""

s = "Hello, world."

print(str(s))   # Hello, world.
print(repr(s))  # 'Hello, world.'


"""
repr() often includes additional syntax information.
"""

x = 1 / 7

print(str(x))   # 0.14285714285714285
print(repr(x))  # 0.14285714285714285


# Example showing repr() usage
x = 10 * 3.25
y = 200 * 200

print("The value of x is " + repr(x) + ", and y is " + repr(y) + "...")


# Strings show clear differences
hello = "hello, world\n"

print(str(hello))   # prints newline
print(repr(hello))  # shows escape sequence


# =========================================
# 1.6 Using repr() for Debugging
# =========================================
"""
repr() is useful because it returns a representation
that could be used to recreate the object.
"""

print(repr((x, y, ("spam", "eggs"))))
# Outputs: (32.5, 40000, ('spam', 'eggs'))


# =========================================
# 1.7 Template Strings (string.Template)
# =========================================
"""
The string module provides a simpler substitution system.

It uses $placeholders instead of {}.
"""

from string import Template

t = Template("Hello $name, welcome to $place")

result = t.substitute(name="Alice", place="Python")

print(result)
# Outputs: Hello Alice, welcome to Python


"""
Template strings:
- Are simpler to use
- Provide less formatting control
- Are useful for basic substitution tasks
"""


# =========================================
# 1.8 Key Idea
# =========================================
"""
Python offers multiple formatting approaches:

- f-strings → modern and concise
- str.format() → flexible and explicit
- concatenation → manual control
- repr() → debugging representation
- Template → simple substitution

Choose based on your needs.
"""


# =========================================
# 1.9 Summary
# =========================================
"""
Fancier output formatting allows you to:

- Insert values into strings
- Control appearance and layout
- Format numbers and percentages

Best practices:
- Use f-strings for most cases
- Use repr() for debugging
- Use Template for simple substitution

Core idea:
"Present data clearly and meaningfully"
"""