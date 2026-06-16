# =========================================
# 1. Lists
# =========================================
"""
A list is an ordered, mutable collection of items.

Items are stored by position (index), can be of any type, and can be
added, changed and removed after the list is created.

This section covers:
- Creating a list
- Adding items with append() and insert()
- Deleting items
- Indexing and slicing
- Concatenating lists
- Mutability
- Copying (assignment vs slicing)
- Using len()
- Nested lists
- List comprehensions
- Sorting
"""


# =========================================
# 1.1 Creating a List
# =========================================
"""
A list is written with square brackets, listing its items separated by
commas.
"""

# create a list of squares
squares = [1, 4, 9, 16, 25]
print(squares)


# =========================================
# 1.2 Adding Items with append() and insert()
# =========================================
"""
Start with an empty list and build it up:
- append() adds an item to the end
- insert() adds an item at a given position
You can also overwrite an item by assigning to its index.
"""

# start with an empty list and append
users = []
users.append('val')
users.append('bob')
users.append('mia')
users.insert(3, 'bea') # append by position
users[0] = 'valentina'  # change value by index


# =========================================
# 1.3 Deleting Items
# =========================================
"""
There are several ways to remove items:
- del removes by index
- remove() removes by value
- pop() removes by index and returns the removed value
"""

# delete items from list
del users[-1]  # delete last item
users.remove('bob')  # delete by value
users.pop(0)  # delete by index and return the value


# =========================================
# 1.4 Indexing and Slicing
# =========================================
"""
Index a list to read a single element (negative indexes count from the
end). Slicing with start:stop returns a new list of elements; the stop
index is not included. You can omit either end, and use a step to skip
elements.
"""

#index & slice list
squares[0]  # first element
squares[-1] # last element

squares[0:2] # elements from index 0 to 2 (not including 2)
squares[:3]  # first three elements
squares[3:]  # elements from index 3 to the end
squares[:]   # all elements
squares[::2] # every other element
squares[-1]  # last element


# =========================================
# 1.5 Concatenating Lists
# =========================================
"""
The + operator joins two lists together into a new list.
"""

# concatenate lists
squares + [36, 49, 64, 81, 100]


# =========================================
# 1.6 Mutability
# =========================================
"""
Lists are mutable, meaning their contents can be changed in place. Here
an incorrect element is replaced by assigning to its index.
"""

# lists are mutable
cubes = [1, 8, 27, 65, 125] # something is wrong here
cubes[3] = 64  # replace the wrong value


# =========================================
# 1.7 Copying: Assignment vs Slicing
# =========================================
"""
Assigning a list to another variable does not copy the data; both names
point to the same list object. Taking a full slice ([:]) creates a new,
independent copy.
"""

#list assignment never copies data
rgb = ["Red", "Green", "Blue"]
rgba = rgb
id(rgb) == id(rgba)  # True, both variables point to the same list object

# a slice operation creates a new list
rgba = rgb[:]  # creates a new list that is a copy of rgb
id(rgb) == id(rgba)  # False, rgb and rgba are different objects


# =========================================
# 1.8 Using len()
# =========================================
"""
len() returns the number of items in a list.
"""

# using len with lists
letters = ['a', 'b', 'c', 'd', 'e']
len(letters)  # returns 5


# =========================================
# 1.9 Nested Lists
# =========================================
"""
A list can contain other lists as its elements, allowing you to build
structures such as a list of lists.
"""

# nested lists
a = ['a', 'b', 'c']
n = [1, 2, 3]
x = [a, n]


# =========================================
# 1.10 List Comprehensions
# =========================================
"""
A list comprehension builds a new list in a single, readable line, using
the form:

    [expression for item in iterable if condition]
"""

# list comprehensions - [expression for item in iterable if condition]
squares = [x**2 for x in range(1, 11)]
print(squares)


# =========================================
# 1.11 Sorting a List
# =========================================
"""
sort() orders the list in place (permanently). Passing reverse=True
sorts in descending order.
"""

# sorting a list
users = ['val', 'bob', 'mia', 'ron', 'ned']
users.sort()  # sorts the list permanently
users.sort(reverse=True)  # sorts in reverse order


