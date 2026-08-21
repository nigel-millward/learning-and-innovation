# =========================================
# 1. Function Annotations
# =========================================
"""
Function annotations are completely optional metadata information about the types used by
user-defined functions.

Annotations are stored on the function's __annotations__ attribute and do not affect how the
function runs.
"""

def function(ham: str, eggs: str = 'eggs') -> str:
    print("Annotations:", function.__annotations__)
    print("Arguments:", ham, eggs)
    return ham + ' and ' + eggs

function('spam')
