# FASTER CODE EXECUTION
# =======================

# 1. INTRO
# ========
# Python has a reputation as a slow language. For example, a regular loop in Python is orders of magnitude slower
# than a similar loop in C. This drawback is countered in several ways. Often programmer productivity is more important
# than code execution time.

#Python is also very capable of wrapping libraries written in faster languages. For example, calculations done in NumPy
# are much faster than similar calculations done in pure Python. Matched with the ease of developing code, this makes
# Python a strong contender in the data science space.

#Still, there’s been a push toward making the core Python language faster. In the fall of 2020, Mark Shannon suggested
# several performance improvements that could be implemented in Python. The proposal, which is known as the
# Shannon Plan, is very ambitious and hopes to make Python five times faster over several releases.


# 2. MEASURE THE PERFORMANCE OF YOUR CODE
# ====================================
""" In general, there are three approaches that you’ll use to measure code performance:

    1. Benchmark small pieces of code that are important in your program.
    2. Profile your program to find bottlenecks that can be improved.
    3. Monitor the performance of your full program.

Typically, you want to do all of these.

Benchmarks can help you choose between different implementations while you’re
developing your code. Python has built-in support for micro-benchmarking with the timeit module. The third-party
 richbench tool is nice for benchmarking functions. Additionally, pyperformance is the benchmark suite used by the
 Faster CPython project to measure improvements.

It’s useful to profile your code if you need to speed up your program and want to figure out which part of your code
to focus on. Python’s standard library provides cProfile, which you can use to collect statistics about your program,
and pstats, which you can use to explore those statistics.

The third approach, monitoring your program’s runtime, is something that you should do with all your programs that run
 for more than a few seconds. The simplest approach is to add a timer in your log messages. The third-party codetiming
  allows you to do this, for example by adding a decorator to your main function.

One approachable and essential way you can contribute to making Python faster is by sharing benchmarks
exemplifying your use cases. Especially if you don’t notice much speedup in Python 3.11, it would be helpful
for the core developers if you’re able to share your code. See Mark Shannon’s lightning talk, How you can help
speed up Python, for more information."""