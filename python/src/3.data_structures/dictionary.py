# create a dictionary
alien_0 = {'color': 'green', 'points': 5}

# Getting the value associated with a key
print(alien_0['color'])
print(alien_0['points'])

# Getting the value with get()
alien_color = alien_0.get('color')
alien_points = alien_0.get('points', 0)
print(alien_color)
print(alien_points)

# Adding a key pair
alien_0['x'] = 0
alien_0['y'] = 25
alien_0['speed'] = 1.5

# Adding to blank dictionary
alien_1 = {}
alien_1['color'] = 'yellow'
alien_1['points'] = 10

# Modifying values in a dictionary
alien_0['color'] = 'yellow'  # change color to yellow
alien_0['points'] = 15  # change points to 15

# Deleting a key-value pair
del alien_0['points']

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

# Nesting a list in a dictionary
favourite_languages = {}
favourite_languages['Nige'] = ['python', 'java', 'scala']
favourite_languages['Bob'] = ['node', 'javascript']

for name, languages in favourite_languages.items():
    print (f'{name}\'s favourite languages are:')
    for language in languages:
        print(f'{language} ')
        
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


# Comprehensions as a shorthand way to create new lists or dictionaries. 
# They let you turn several lines of code into a single, readable line
# Result: [1, 4, 9, 16]

numbers = [1, 2, 3, 4]
squared = []

for n in numbers:
    squared.append(n * n)


# Using a dictionary comprehension
# Result: {1: 1, 2: 4, 3: 9, 4: 16}
'''
n: n * n: What you want to do (the result).
for n in numbers: Where the data is coming from.
'''
squared_dictionary = {n: n * n for n in numbers}

# approach for complex comprehensions
''' Don't do this!'''
clean_names = [name.strip().capitalize() for name in [" alice", "BOB ", " charlie "] if len(name.strip()) > 3]

def format_name(name):
    stripped = name.strip()
    return stripped.capitalize()

names = [" alice", "BOB ", " charlie "]
clean_names = [format_name(n) for n in names if len(n.strip()) > 3]