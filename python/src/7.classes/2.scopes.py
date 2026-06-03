# 1 Python Scope
'''
In Python, scopes determine the visibility and lifetime of your variables 
by following a strict lookup order called the LEGB rule, which stands for 
Local, Enclosing, Global, and Built-in.
'''

# 2, LEGB rule explained
#Python resolves variable names by searching through namespaces from the inside out

'''
   [ Built-In Scope: len(), range(), ValueError ]
         ▲
   [ Global Scope: Module-level variables, functions ]
         ▲
   [ Enclosing Scope: Outer function in nested setups ]
         ▲
   [ Local Scope: Inside the current function ]


Local (L): Variables defined directly inside the current function. They are created when the function is called and disappear when it returns.
Enclosing (E): Variables inside an outer function when you have nested functions (also called closures).
Global (G): Variables defined at the top level of a file or module. They are accessible anywhere within that specific file.
Built-in (B): Keywords, functions, and exceptions built right into Python (e.g., print(), len(), dict).

'''

# 3. Local vs Global scope example
x = "global"  # Global scope

def my_func():
    x = "local"  # Local scope
    print(x)     # Looks locally first

my_func()        # Prints: local
print(x)         # Prints: global

# 4. Enclosing scope example
def outer_func():
    message = "Hello from outer"  # Enclosing scope
    
    def inner_func():
        print(message)            # Looks Local (none) -> Enclosing (found!)
        
    inner_func()
    
    
outer_func()  # Prints: Hello from outer

# 5. Modifying variables across scopes
'''
By default, Python treats any variable assigned inside a function as a local variable. 
If you want to modify a variable in a higher scope rather than creating a new local one, 
you must explicitly use a keyword:

global: Declares that a variable inside a function belongs to the file's top level.
nonlocal: Declares that a variable inside a nested function belongs to the outer enclosing function.

'''
# 6. Global variable example
"""Without global: Python would raise an UnboundLocalError because it sees counter += 1 
and assumes you are trying to create a new local variable before assigning it a starting value.
"""

# A variable defined at the top level of the file
counter = 0  

def increment_global():
    global counter  # Links to the file-level variable
    counter += 1    # Directly modifies the global counter
    print(f"Inside function: {counter}")

increment_global()  # Prints: Inside function: 1
print(f"Outside function: {counter}")  # Prints: Outside function: 1


# 7. Local variable example
"""Without nonlocal: inner_function would create a completely separate, local variable named score. 
The outer function's score would remain unchanged at 10.
"""
def outer_function():
    # Variable inside the outer function (enclosing scope)
    score = 10  

    def inner_function():
        nonlocal score  # Links to the outer function's variable
        score = 50      # Modifies the variable in the outer function
        print(f"Inner function score: {score}")

    inner_function()
    print(f"Outer function score: {score}")

outer_function()
# Prints:
# Inner function score: 50
# Outer function score: 50
