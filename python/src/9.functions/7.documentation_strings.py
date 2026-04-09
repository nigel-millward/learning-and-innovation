## Document string conventions
'''
- The first line should always be a short, concise summary of the objects purpose.
- The second line should be blank.
- The following lines should be one or more paragraphs describing the object’s calling conventions, its side effects, etc.  
'''

# 1. Example of a function with a docstring
def my_function():
    """Do nothing, but document it.

    No, really, it doesn't do anything:

        >>> my_function()
        >>>
    """
    pass

print(my_function.__doc__)
