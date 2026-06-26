# =========================================
# 1. Performance Measurement
# =========================================
"""
Performance measurement allows you to compare different approaches
and understand how efficiently your code runs.

Python provides tools to:
- Measure execution time precisely
- Compare alternative implementations
- Identify slow sections in larger programs
"""


# =========================================
# 1.1 Measuring Small Code Snippets (timeit)
# =========================================
"""
The timeit module is designed for precise timing of small pieces of code.

It runs code multiple times to produce reliable results.
"""

from timeit import Timer

# Traditional swap
t1 = Timer("t=a; a=b; b=t", "a=1; b=2").timeit()

# Tuple unpacking swap
t2 = Timer("a, b = b, a", "a=1; b=2").timeit()

print(t1)
print(t2)


"""
Example output:

0.57535828626024577
0.54962537085770791

Conclusion:
- Tuple unpacking is slightly faster
"""


# =========================================
# 1.2 Why Use timeit?
# =========================================
"""
timeit is preferred because:

- It runs code many times for accuracy
- It reduces impact of system noise
- It isolates the code being measured
"""


# =========================================
# 1.3 Basic timeit Usage
# =========================================
"""
You can measure any small snippet of Python code.
"""

from timeit import timeit

result = timeit("sum(range(100))", number=10000)

print(result)


"""
Arguments:
- statement → code to run
- number → how many times to run it
"""


# =========================================
# 1.4 Comparing Approaches
# =========================================
"""
timeit is useful for comparing alternatives.

Example:
"""

from timeit import timeit

t1 = timeit("[x*x for x in range(100)]", number=10000)
t2 = timeit("list(map(lambda x: x*x, range(100)))", number=10000)

print(t1, t2)


"""
This helps choose the faster implementation.
"""


# =========================================
# 1.5 Profiling Larger Programs (profile)
# =========================================
"""
For larger programs, use profiling tools.

The profile module identifies which parts of the code
take the most time.
"""

import profile

def slow_function():
    total = 0
    for i in range(1000):
        for j in range(1000):
            total += i * j
    return total

# profile.run("slow_function()")


"""
Output shows:
- Function call counts
- Time spent in each function
"""


# =========================================
# 1.6 Analysing Results (pstats)
# =========================================
"""
The pstats module helps analyse profiling data.

It allows:
- Sorting by execution time
- Viewing most expensive functions
"""

# Typical usage (after profiling):
# import pstats
# stats = pstats.Stats("output.prof")
# stats.sort_stats("time").print_stats()


# =========================================
# 1.7 When to Use Each Tool
# =========================================
"""
Use:

- timeit → small, focused comparisons
- profile → large programs
- pstats → analyse profiling results
"""


# =========================================
# 1.8 Common Use Cases
# =========================================
"""
Performance measurement is useful for:

- Optimising code
- Comparing algorithms
- Finding bottlenecks
- Improving scalability
"""


# =========================================
# 1.9 Key Idea
# =========================================
"""
Measure performance before optimising.

Good practice:
- Identify slow areas first
- Optimise only where necessary
- Prefer readable code unless performance matters
"""


# =========================================
# 1.10 Summary
# =========================================
"""
Core tools:

- timeit → measure execution time
- Timer → precise timing control
- profile → analyse program performance
- pstats → interpret profiling data

Best practices:
- Use timeit for small benchmarks
- Use profiling for large codebases
- Optimise based on evidence

Core idea:
"Measure first, optimise second"
"""