x = int(input("Please enter an integer: "))
if x < 0:
    x = 0
    print('Negative changed to zero')
elif x == 0:
    print('Zero')
elif x == 1:
    print('Single')
elif x > 1:
    print('More than 1')
    
    
# in keyword
reply = input("Do you want to continue? (y/n): ").lower()
if reply in {'y', 'ye', 'yes'}:
    pass