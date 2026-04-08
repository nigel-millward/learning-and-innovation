## Lambda expressions are small anonymous functions that can be created with the lambda keyword
## lambda arguments: expression

# 1. regualar way
def add_five(x):
    return x + 5

print(add_five(10)) # Output: 15

# 2. lambda way
add_five = lambda x: x + 5
print(add_five(10)) # Output: 15

# 3 When do you use lambda functions?
'''
You’ll rarely use lambdas on their own like the example above. 
They shine when you need to pass a tiny bit of logic into another function, like sorting or filtering.
'''

# 3.1 Custom Sorting
data = [("Alice", 25), ("Bob", 20), ("Charlie", 30)]
data.sort(key=lambda person: person[1]) # We tell Python: "Sort this by the second item (index 1) in each tuple"
print(data) # Output: [('Bob', 20), ('Alice', 25), ('Charlie', 30)]

# 3.2 Filtering Lists
numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(lambda x: x % 2 == 0, numbers)) # filter(): Keeps only the items where a function returns True
print(evens) # Output: [2, 4, 6]


# 3.3 Mapping Lists
prices_usd = [10, 25, 50, 100]
prices_eur = list(map(lambda x: x * 0.92, prices_usd)) # map(function, list) - map(): Applies a function to every item in an iterable.
print(prices_eur) # Output: [9.2, 23.0, 46.0, 92.0]


# 4. Golden rules
'''
1. Keep it simple: Lambda functions are meant for small, simple operations.
2. Use them where they make the code more readable, not less.
3. Avoid complex logic inside a lambda; if it gets too complicated, use a regular function.
'''




