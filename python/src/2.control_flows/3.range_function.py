# if you need to iterate over a sequence of numbers, 
# the built-in function range() generates arithmetic progressions.

# range(n) can be used to specify iterations
for i in range(5):
    print(i)
'''
0, 1, 2, 3, 4
'''

# range(n, n) can also be used to specify a start and stop value
for i in range(5, 10):
    print(i)
'''
5, 6, 7, 8, 9
'''

# range(n, n, n) can also specify start, stop and step
for i in range(0, 10, 3):
    print(i)
'''
0, 3, 6, 9
''' 

# iterate over a indices of a sequence
a = ['Mary', 'had', 'a', 'little', 'lamb']
for i in range(len(a)):
    print(i, a[i])
'''
0 Mary
1 had
2 a
3 little
4 lamb
'''

# functions can take iterables as arguments, so can use range() to generate a sequence of numbers to iterate over
sum(range(4))  # 0 + 1 + 2 + 3 = 6


