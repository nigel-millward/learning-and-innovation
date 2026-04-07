## What are keyword arguments?
'''
keyword argument: an argument preceded by an identifier (e.g. name=) in a function call or passed as a value in a dictionary preceded by **.
For example, 3 and 5 are both keyword arguments in the following calls to complex():
complex(real=3, imag=5)
complex(**{'real': 3, 'imag': 5})

positional argument: an argument that is not a keyword argument. Positional arguments can appear at the beginning of an argument list and/or be passed as elements of an iterable preceded by *. 
For example, 3 and 5 are both positional arguments in the following calls:
complex(3, 5)
complex(*(3, 5))
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

# 1. Anything goes
def standard_arg(arg):
    print(arg)
'''
Both of these work
standard_arg(5)              # Positional
standard_arg(arg=5)          # Keyword
'''
   
# 2. Standard keyword arguments
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")


greet("Alice") # Calling with positional arguments, Output: Hello, Alice!
greet(greeting="Hi", name="Bob") # Calling with keyword arguments (order doesn't matter), Output: Hi, Bob!

# 3. Keyword-only arguments
def set_config(filename, *, mode="read-only"):
    print(f"File: {filename}, Mode: {mode}")


set_config("data.csv", mode="write") # Valid call
# set_config("data.csv", "write")  # Invalid call: Raises TypeError


# 4. Arbitrary Positional Arguments
def sum_all(*args):
    return sum(args)

print(sum_all(10, 20, 30)) # You can pass any number of values, Output: 60 (collected as (10, 20, 30))

# 5. Arbitrary Keyword Arguments
def display_profile(user, **details):
    print(f"User: {user}")
    for key, value in details.items():
        print(f"- {key}: {value}")
        
display_profile("jdoe", email="jd@example.com", location="NYC") # Passing arbitrary named argument
# Output: User: jdoe, - email: jd@example.com, - location: NYC


# 6.Combining all types of arguments
def complex_function(a, b, *args, c=10, **kwargs):
    print(f"a: {a}, b: {b}, args: {args}, c: {c}, kwargs: {kwargs}")

complex_function(1, 2, 3, 4, c=5, d=6, e=7) # Output: a: 1, b: 2, args: (3, 4), c: 5, kwargs: {'d': 6, 'e': 7}


##################################
   

# 7. The no names allowed (/)
def pos_only_arg(arg, /):
    print(arg)

pos_only_arg(5)              # Works
pos_only_arg(arg=5)          # Error! (TypeError)

# 8. The names required (*)
def kwd_only_arg(*, arg):
    print(arg)

kwd_only_arg(arg=5)          # Works
kwd_only_arg(5)              # Error! (TypeError)

# 9. Combined example
def combined_example(pos_only, /, standard, *, kwd_only):
    print(pos_only, standard, kwd_only)


combined_example(1, 2, kwd_only=3)      # Works!
combined_example(1, standard=2, kwd_only=3) # Also works!
combined_example(pos_only=1, standard=2, kwd_only=3)  # Error! (TypeError)

