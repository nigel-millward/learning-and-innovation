# 1. Measure some strings
words = ['cat', 'window', 'defenestrate']
for w in words:
    print(w, len(w))
    
'''
cat 3
window 6
defenestrate 12
'''


# 2.1 create a sample collection
users = {
    'Hans': 'active',
    'Greta': 'inactive',
    'Fritz': 'active'
}

# 2.2 Strategy: Iterate over a copy
for user, status in users.copy().items():
    if status == 'inactive':
        del users[user]

# 2.3 Strategy: create a new collection
active_users = {}
for user, status in users.items():
    if status == 'active':
        active_users[user] = status
        
# 2.4 Strategy: iterate over number range
for i in range(5):
    print(i)
    
    