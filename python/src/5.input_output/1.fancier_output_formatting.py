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
# Method calls
name = "alice"
print(f"{name.upper()}")    # ALICE

# Ternary/conditional
age = 20
print(f"{'adult' if age >= 18 else 'minor'}")  # adult

"""
Thumb rule: if you have to pause to understand what's inside {}, 
extract it. F-strings are for presentation, not logic.
"""
items = [1, 2, 3, -4, -5]

# Hard to read inline
print(f"{', '.join(str(x) for x in sorted(items) if x > 0)}")

# Better
filtered = ', '.join(str(x) for x in sorted(items) if x > 0)
print(f"{filtered}")

# =========================================
# 1.2 Formatting Numbers in f-strings
# =========================================
"""
F-strings support formatting options inside {} using a colon.
"""

pie = 3.14159
large_value = 123_343_665_123

print(f"{pie:.2f}")   # Outputs: 3.14 (2 decimal places)
print(f"{pie:10.2f}") # Outputs: '      3.14' (width + alignment)
print(f"{large_value:,}") # Outputs: '123,343,665,123' (with thousands separator)

"""
Grouping separators
f"{1234567:,}"     # 1,234,567  (comma)
f"{1234567:_}"     # 1_234_567  (underscore)

Decimal places / notation
f"{3.14159:.2f}"   # 3.14       (fixed decimal places)
f"{3.14159:.4f}"   # 3.1416     (rounds)
f"{12345:.2e}"     # 1.23e+04   (scientific notation)
f"{12345:.2g}"     # 1.2e+04    (general: picks f or e automatically)


Width & alignment
f"{42:10}"         # '        42'  (right-align, width 10)
f"{42:<10}"        # '42        '  (left-align)
f"{42:^10}"        # '    42    '  (centre)
f"{42:0>10}"       # '0000000042'  (pad with zeros)

Sign
f"{42:+}"          # +42   (always show sign)
f"{-42:+}"         # -42
f"{42: }"          # ' 42' (space for positive, - for negative)

Integer bases
f"{255:b}"         # 11111111  (binary)
f"{255:o}"         # 377       (octal)
f"{255:x}"         # ff        (hex lowercase)
f"{255:X}"         # FF        (hex uppercase)
f"{255:#x}"        # 0xff      (with prefix)

Percentage
f"{0.4967:.2%}"    # 49.67%   (multiplies by 100, adds %)

"""



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
- repr() → developer debuggin/logging output

repr = representation
Specifically, it returns the official string representation of an object — 
one that ideally could be pasted back into Python to recreate the object exactly.

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
It is very old (2004), and predates format() and f-strings
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