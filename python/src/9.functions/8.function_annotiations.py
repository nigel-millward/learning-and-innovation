# Function annotations are completely optional metadata information about the types used by user-defined functions

def function(ham: str, eggs: str = 'eggs') -> str:
    print("Annotations:", function.__annotations__)
    print("Arguments:", ham, eggs)
    return ham + ' and ' + eggs

function('spam')