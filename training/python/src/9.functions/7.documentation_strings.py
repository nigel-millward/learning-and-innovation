# =========================================
# 1. Documentation Strings
# =========================================
"""
Documentation strings (docstrings) describe what an object does and are accessible at runtime
via the __doc__ attribute.

Document string conventions:
- The first line should always be a short, concise summary of the objects purpose.
- The second line should be blank.
- The following lines should be one or more paragraphs describing the object's calling conventions, its side effects, etc.
"""

# Example of a function with a docstring
def my_function():
    """Do nothing, but document it.

    No, really, it doesn't do anything:

        >>> my_function()
        >>>
    """
    pass

print(my_function.__doc__)
