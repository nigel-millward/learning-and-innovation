# =========================================
# 1. Mathematics
# =========================================
"""
Python provides several built-in modules for working with numerical data.

Key modules:
- math → mathematical functions
- random → random number generation
- statistics → statistical calculations
"""


# =========================================
# 1.1 The math Module
# =========================================
"""
The math module provides access to mathematical functions.

These are implemented in C and are efficient and reliable.
"""

import math

print(math.cos(math.pi / 4))
# Outputs: 0.7071067811865476

print(math.log(1024, 2))
# Outputs: 10.0


"""
Common functions:
- math.sqrt(x) → square root
- math.sin(x), math.cos(x), math.tan(x)
- math.log(x, base)
- math.pi → constant π
"""


# =========================================
# 1.2 The random Module
# =========================================
"""
The random module provides tools for generating random values.

Useful for:
- simulations
- games
- sampling data
"""

import random

# Random selection
print(random.choice(["apple", "pear", "banana"]))
# Example output: 'apple'

# Random sample (no duplicates)
print(random.sample(range(100), 10))
# Example: [30, 83, 16, ...]

# Random float between 0.0 and 1.0
print(random.random())
# Example: 0.1797...

# Random integer from range
print(random.randrange(6))
# Example: 4


# =========================================
# 1.3 Random Generation Notes
# =========================================
"""
Key behaviours:

- random.choice() → selects one item
- random.sample() → selects unique items
- random.random() → float in [0.0, 1.0)
- random.randrange(n) → integer from 0 to n-1
"""


# =========================================
# 1.4 The statistics Module
# =========================================
"""
The statistics module provides basic statistical calculations.
"""

import statistics

data = [2.75, 1.75, 1.25, 0.25, 0.5, 1.25, 3.5]

print(statistics.mean(data))
# Outputs: 1.6071428571428572

print(statistics.median(data))
# Outputs: 1.25

print(statistics.variance(data))
# Outputs: 1.3720238095238095


"""
Common functions:
- mean() → average
- median() → middle value
- variance() → spread of data
"""


# =========================================
# 1.5 When to Use Each Module
# =========================================
"""
Use:

- math → precise calculations (trigonometry, logs)
- random → randomness and sampling
- statistics → analysing numeric data
"""


# =========================================
# 1.6 Advanced Numerical Libraries
# =========================================
"""
For more advanced numerical work:

- SciPy → scientific computing
- NumPy → fast array operations

These are external libraries commonly used in data science.
"""


# =========================================
# 1.7 Key Idea
# =========================================
"""
Python provides a range of tools for working with numbers:

- math → computation
- random → unpredictability
- statistics → analysis

Each module is designed for a specific purpose.
"""


# =========================================
# 1.8 Summary
# =========================================
"""
Core modules:

- math → mathematical functions
- random → random numbers and sampling
- statistics → data analysis

Best practices:
- Use math for numerical precision
- Use random for simulations and sampling
- Use statistics for analysing datasets

Core idea:
"Choose the right tool for working with numerical data"
"""
