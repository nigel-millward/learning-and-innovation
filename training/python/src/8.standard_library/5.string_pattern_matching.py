# =========================================
# 1. String Pattern Matching (re)
# =========================================
"""
The re module provides tools for working with regular expressions.

Regular expressions allow you to:
- Search for complex patterns in text
- Extract matching data
- Modify strings efficiently

They are powerful but can be harder to read than simple string methods.
"""


# =========================================
# 1.1 Importing the re Module
# =========================================
"""
To use regular expressions, import the re module.
"""

import re


# =========================================
# 1.2 Finding Patterns (findall)
# =========================================
"""
re.findall(pattern, string) returns all matches of a pattern.
"""

result = re.findall(r"\bf[a-z]*", "which foot or hand fell fastest")

print(result)
# Outputs: ['foot', 'fell', 'fastest']


"""
Pattern explanation:
- \b       → word boundary
- f        → word starts with 'f'
- [a-z]*   → followed by any letters
"""


# =========================================
# 1.3 Replacing Text (sub)
# =========================================
"""
re.sub(pattern, replacement, string) replaces matching patterns.
"""

result = re.sub(r"(\b[a-z]+) \1", r"\1", "cat in the the hat")

print(result)
# Outputs: cat in the hat


"""
Pattern explanation:
- (\b[a-z]+) → capture a word
- \1         → refers to the captured word
- replaces repeated words with a single occurrence
"""


# =========================================
# 1.4 Common Regular Expression Patterns
# =========================================
"""
Some useful patterns:

- .      → any character
- *      → zero or more repetitions
- +      → one or more repetitions
- ?      → optional
- \d     → digit
- \w     → word character
- \s     → whitespace
"""

# Example: find all numbers
print(re.findall(r"\d+", "Order 123, item 456"))
# Outputs: ['123', '456']


# =========================================
# 1.5 Raw Strings (r"...")
# =========================================
"""
Regular expressions use backslashes (\).

To avoid escaping issues, use raw strings (prefix with 'r').
"""

pattern = r"\d+"  # Correct
# pattern = "\\d+"  # Equivalent but harder to read


# =========================================
# 1.6 When to Use Regular Expressions
# =========================================
"""
Use regular expressions when:
- Patterns are complex
- You need advanced matching
- You are extracting structured data

Examples:
- Validating emails
- Parsing logs
- Cleaning text data
"""


# =========================================
# 1.7 When to Use String Methods Instead
# =========================================
"""
For simple tasks, prefer built-in string methods.

They are:
- Easier to read
- Easier to debug
"""

result = "tea for too".replace("too", "two")

print(result)
# Outputs: tea for two


"""
Use string methods for:
- Simple replacements
- Basic searches
- Clear, readable code
"""


# =========================================
# 1.8 Key Idea
# =========================================
"""
Regular expressions are powerful for complex text processing.

However:
- They are harder to read
- They should be used only when needed

Prefer simpler string methods whenever possible.
"""


# =========================================
# 1.9 Summary
# =========================================
"""
Core tools:

- re.findall() → extract matches
- re.sub() → replace patterns

Best practices:
- Use raw strings for patterns
- Use regex for complex matching
- Use string methods for simple tasks

Core idea:
"Use the simplest tool that solves the problem"
"""