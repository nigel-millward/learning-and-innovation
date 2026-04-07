## arguments are already in a list or tuple 
# but need to be unpacked for a function call requiring separate positional arguments

# 1.  unpack listss
args = [3,6]
list(range(*args))  # [0, 1, 2, 3, 4, 5]


# 2. unpack dictionaries
def parrot(voltage, state='a stiff', action='voom'):
    print("-- This parrot wouldn't", action, end=' ')
    print("if you put", voltage, "volts through it.", end=' ')
    print("E's", state, "!")
    
d = {"voltage": "four million", "state": "bleedin' demised", "action": "VOOOOM"}
parrot(**d)
