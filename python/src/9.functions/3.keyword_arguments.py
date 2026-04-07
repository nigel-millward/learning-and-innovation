## What are keyword arguments?
'''
explicit positional: These are arguments passed to a function by position (i.e., the order in which they are defined in the function signature).
keyword argument: Keyword Arguments: These are arguments passed to a function preceded by an identifier (e.g., name="Alice").
'''

## What are benefits of using keyword arguments?
'''
1.Clarity: Keyword arguments make it clear what each argument represents, improving readability.
    - Without solver(100,20,5)
    - With solver(price=100, tax_rate=0.20, discount=5)
2. Order doesnt matter: 
    - They allow arguments to be passed in any order, making function calls more flexible.
3. Skip optional arguments: 
    - They allow you to skip optional arguments and only specify the ones you want to change from their default values.
'''

# 1.1 Standard keyword arguments
def standard_arg(arg):
    print(arg)
    
standard_arg(arg=5) # Explicit keyword argument, Output: 5


# 1.2 Standard keyword arguments
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet(greeting="Hi", name="Bob") # Calling with keyword arguments (order doesn't matter), Output: Hi, Bob!

# 2. Standard positional argument
def add(x, y):
    return x + y    
print(add(2, 3)) # Output: 5


# 3. Arbitary arguments
'''
*args (Positional): This syntax collects any extra positional arguments (those passed by value/order, not by name) into a tuple.
**kwargs (Keyword): This syntax collects any extra keyword arguments into a dictionary, where keys are the argument names and values are the passed data.

'''

# 4. Arbitary Keyword Arguments
def display_profile(user, **details):
    print(f"User: {user}")
    for key, value in details.items():
        print(f"- {key}: {value}")
        
display_profile("jdoe", email="jd@example.com", location="NYC") # Passing arbitrary keyword argument


#5 Arbitrary Argument Lists
def sum_numbers(file, separator, *args):
    return file.write(separator.join(args))

print(sum_numbers(1, 2, 3, 4)) # Output: 10

# 6.Combining all types of arguments
def complex_function(a, b, *args, c=10, **kwargs):
    print(f"a: {a}, b: {b}, args: {args}, c: {c}, kwargs: {kwargs}")

complex_function(1, 2, 3, 4, c=5, d=6, e=7) # Output: a: 1, b: 2, args: (3, 4), c: 5, kwargs: {'d': 6, 'e': 7}
