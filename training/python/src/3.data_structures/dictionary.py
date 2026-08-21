# =========================================
# 1. Dictionaries
# =========================================
"""
A dictionary stores data as key-value pairs.

Each key maps to a value, letting you look data up by a meaningful name
rather than by position. Dictionaries are mutable, so you can add, change
and remove pairs after creation.

This section covers:
- Creating a dictionary
- Accessing values by key
- Accessing values safely with get()
- Adding key-value pairs
- Modifying values
- Deleting key-value pairs
- Looping through items, keys and values
- Nesting (lists of dictionaries, lists in dictionaries, dictionaries of dictionaries)
- Comprehensions
"""


# =========================================
# 1.1 Creating a Dictionary
# =========================================
"""
A dictionary is written with curly braces, listing key-value pairs
separated by commas. Each pair uses the form key: value.
"""

# create a dictionary
alien_0 = {'color': 'green', 'points': 5}


# =========================================
# 1.2 Accessing Values by Key
# =========================================
"""
To read a value, index the dictionary with its key.

If the key does not exist this raises a KeyError.
"""

# Getting the value associated with a key
print(alien_0['color'])
print(alien_0['points'])


# =========================================
# 1.3 Accessing Values Safely with get()
# =========================================
"""
get() returns the value for a key, but does not raise an error if the
key is missing. You can optionally supply a default value to return
instead (here 0 for 'points').
"""

# Getting the value with get()
alien_color = alien_0.get('color')
alien_points = alien_0.get('points', 0)
print(alien_color)
print(alien_points)


# =========================================
# 1.4 Adding Key-Value Pairs
# =========================================
"""
You can add a new pair simply by assigning to a new key. This works on an
existing dictionary, and also on a brand new empty dictionary.
"""

# Adding a key pair
alien_0['x'] = 0
alien_0['y'] = 25
alien_0['speed'] = 1.5

# Adding to blank dictionary
alien_1 = {}
alien_1['color'] = 'yellow'
alien_1['points'] = 10


# =========================================
# 1.5 Modifying Values
# =========================================
"""
Assigning to a key that already exists replaces its current value.
"""

# Modifying values in a dictionary
alien_0['color'] = 'yellow'  # change color to yellow
alien_0['points'] = 15  # change points to 15


# =========================================
# 1.6 Deleting Key-Value Pairs
# =========================================
"""
del removes a key and its value from the dictionary permanently.
"""

# Deleting a key-value pair
del alien_0['points']


# =========================================
# 1.7 Looping Through a Dictionary
# =========================================
"""
You can loop over a dictionary in three ways:
- items() gives you each key and value together
- keys() gives you just the keys
- values() gives you just the values
"""

# Looping through all key-value pairs
favourite_languages = {
'jen': 'python',
'sarah': 'c',
'edward': 'ruby',
'phil': 'python',
}

for name, language in favourite_languages.items():
    print(f'name: {name}, language: {language} ')

# Looping through the keys
for name in favourite_languages.keys():
    print(f'name: {name}')

# Looping through the values
for language in favourite_languages.values():
    print(f'language: {language}')


# =========================================
# 1.8 Nesting a List of Dictionaries
# =========================================
"""
Dictionaries can be stored inside a list, which is useful when you have
many similar records (for example, a list of users). You can append
dictionaries one at a time, or define the whole list at once, then loop
through each dictionary in turn.
"""

# Nesting a list of dictionaries
users = []

new_user = {
    'username': 'mrAnderson',
    'first': 'neo',
    'last': 'anderson',
}

users.append(new_user)

users = [
    {
        'username': 'mrAnderson',
        'first': 'neo',
        'last': 'anderson',
    },
    {
        'username': 'trinny',
        'first': 'trinity',
        'last': '',
    },
    {
        'username': 'morph',
        'first': 'morpheus',
        'last': '',
    },
]

for user in users:
    for key, value in user.items():
        print(f'{key}: {value}')
    print('\n')


# =========================================
# 1.9 Nesting a List in a Dictionary
# =========================================
"""
A value in a dictionary can itself be a list. This lets you associate
multiple items with a single key, then loop through that inner list.
"""

# Nesting a list in a dictionary
favourite_languages = {}
favourite_languages['Nige'] = ['python', 'java', 'scala']
favourite_languages['Bob'] = ['node', 'javascript']

for name, languages in favourite_languages.items():
    print (f'{name}\'s favourite languages are:')
    for language in languages:
        print(f'{language} ')


# =========================================
# 1.10 Nesting a Dictionary of Dictionaries
# =========================================
"""
A value in a dictionary can also be another dictionary. This is useful
for storing detailed information about each entry, keyed by an
identifier such as a username.
"""

# nesting a dictionary of dictionaries
users = {
    'bbuilder': {
        'first': 'bob',
        'last': 'builder',
        'location': 'bobsville',
    },
    'ttankengine': {
        'first': 'thomas',
        'last': 'tankengine',
        'location': 'island of sodor',
    }
}

for username, user_info in users.items():
    print(f'Username: {username}')
    full_name = f"{user_info['first']} {user_info['last']}"
    location = user_info['location']
    print(f'\tFull name: {full_name.title()}')


# =========================================
# 1.11 Comprehensions
# =========================================
"""
Comprehensions are a shorthand way to create new lists or dictionaries.
They let you turn several lines of code into a single, readable line.

A list comprehension here produces: [1, 4, 9, 16]
A dictionary comprehension produces: {1: 1, 2: 4, 3: 9, 4: 16}

The dictionary comprehension reads as:
- n: n * n   What you want to do (the result).
- for n in numbers   Where the data is coming from.

For complex comprehensions, prefer extracting the logic into a helper
function rather than cramming everything onto one line.
"""

# Comprehensions as a shorthand way to create new lists or dictionaries.
# They let you turn several lines of code into a single, readable line
# Result: [1, 4, 9, 16]

numbers = [1, 2, 3, 4]
squared = []

for n in numbers:
    squared.append(n * n)


# Using a dictionary comprehension
# Result: {1: 1, 2: 4, 3: 9, 4: 16}
"""
n: n * n: What you want to do (the result).
for n in numbers: Where the data is coming from.
"""
squared_dictionary = {n: n * n for n in numbers}

# approach for complex comprehensions
""" Don't do this!"""
clean_names = [name.strip().capitalize() for name in [" alice", "BOB ", " charlie "] if len(name.strip()) > 3]

def format_name(name):
    stripped = name.strip()
    return stripped.capitalize()

names = [" alice", "BOB ", " charlie "]
clean_names = [format_name(n) for n in names if len(n.strip()) > 3]
