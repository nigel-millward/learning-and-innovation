# =========================================
# 1. pass Statements
# =========================================
"""
The pass statement does nothing. It can be used when a statement is required
syntactically but the program requires no action.

This section shows pass used in:
- A function definition
- A loop
- A class definition
"""


# =========================================
# 1.1 pass in a Function Definition
# =========================================
"""
pass acts as a placeholder body for a function that does not yet do anything.
"""

# Example 1: Using pass in a function definition
def my_function():
    pass  # This function does nothing


# =========================================
# 1.2 pass in a Loop
# =========================================
"""
pass can serve as the body of a loop when no action is needed on each iteration.
"""

# Example 2: Using pass in a while loop
for i in range(5):
    pass  # This loop does nothing


# =========================================
# 1.3 pass in a Class Definition
# =========================================
"""
pass lets you define a minimal class with no attributes or methods.
"""

# Example 3: Using pass in a class definition
class MyEmptyClass:
    pass  # This class has no attributes or methods

