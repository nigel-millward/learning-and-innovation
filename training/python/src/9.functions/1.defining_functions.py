# =========================================
# 1. Defining Functions
# =========================================
"""
A Python function is a reusable block of code designed to perform a single, specific action.

This module covers:
- Defining a function with the def keyword
- Choosing between functions and classes
"""


# =========================================
# 1.1 Defining a Function
# =========================================
"""
You define a function using the def keyword.
"""

def greet_user(name):
    """Display a simple greeting."""
    print(f"Hello, {name.title()}!")

greet_user('alice')  # Output: Hello, Alice!


# =========================================
# 1.2 Functions vs Classes
# =========================================
"""
The Golden Rule: Start with a function. Only move to a class when
- your functions start getting messy
- or you feel like you're constantly repeating the same data structures

Function:
- task is stateless: You dont need the code to remember what happened the last time it ran
- Simplicity:  If you can run a quick script to accomplish a task, a function is often the best choice.

Class:
- you need to maintain state
- you have a is-a relationship: like Animal and Cat, Dog
"""
