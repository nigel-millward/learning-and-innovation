"""
The biggest change in Python 3.8 is the introduction of assignment expressions.
They are written using a new notation (:=).
This operator is often called the walrus operator
as it resembles the eyes and tusks of a walrus on its side.
"""

# 3.7 if you want to assign to a variable and print its value, then you typically do something like this:
walrus = False
print(walrus)

# assignment expression
print(walrus := True)

# can be used in while loops.

#3.7
inputs = list()
while True:
    current = input("Write something: ")
    if current == "quit":
        break
    inputs.append(current)

# becomes
inputs = list()
while (current := input("Write something: ")) != "quit":
    inputs.append(current)
