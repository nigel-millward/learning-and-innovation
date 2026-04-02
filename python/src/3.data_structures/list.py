# create a list of squares
squares = [1, 4, 9, 16, 25]
print(squares)

#index & slice list
squares[0]  # first element
squares[-1] # last element

squares[0:2] # elements from index 0 to 2 (not including 2)
squares[:3]  # first three elements
squares[3:]  # elements from index 3 to the end 
squares[:]   # all elements 
squares[::2] # every other element  
squares[-1]  # last element

# concatenate lists
squares + [36, 49, 64, 81, 100]

# lists are mutable
cubes = [1, 8, 27, 65, 125] # something is wrong here
cubes[3] = 64  # replace the wrong value

#list assignment never copies data
rgb = ["Red", "Green", "Blue"]
rgba = rgb
id(rgb) == id(rgba)  # True, both variables point to the same list object

# a slice operation creates a new list
rgba = rgb[:]  # creates a new list that is a copy of rgb
id(rgb) == id(rgba)  # False, rgb and rgba are different objects

# using len with lists
letters = ['a', 'b', 'c', 'd', 'e']
len(letters)  # returns 5

# nested lists
a = ['a', 'b', 'c']
n = [1, 2, 3]
x = [a, n]

# list comprehensions - [expression for item in iterable if condition]
squares = [x**2 for x in range(1, 11)]
print(squares)
