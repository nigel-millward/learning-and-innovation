# =========================================
# 1. else Clauses on Loops
# =========================================
"""
In a for or while loop the break statement may be paired with an else clause.
If the loop finishes without executing the break, the else clause executes.

This section includes:
- A for loop where the else clause runs (no break)
- A for loop where the else clause is skipped (break occurs)
- A while loop where the else clause runs (condition becomes False)
- A while loop where the else clause is skipped (break occurs)
"""


# =========================================
# 1.1 for Loop Where the else Clause Runs
# =========================================
"""
The else clause is executed after the loop finishes its final iteration when no
break occurred.
"""

# 1. for loop - the else clause is executed after the loop finishes its final iteration when no break occurred.
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(f"Checking: {fruit}")
else:
    # This runs because the loop finished the entire list
    print("Finished checking all fruits.")


# =========================================
# 1.2 for Loop Where the else Clause Is Skipped
# =========================================
"""
When the loop is interrupted by a break, the else clause does not run.
"""

# 2. for loop example with a break
numbers = [1, 2, 3, 4, 5]

for n in numbers:
    if n == 3:
        print("Found 3! Breaking now.")
        break
else:
    print("This will NOT print because of the break.")


# =========================================
# 1.3 while Loop Where the else Clause Runs
# =========================================
"""
The else block runs as soon as the loop condition becomes False.
"""

# 3. while loop - the else block runs as soon as the loop condition becomes False
count = 3

while count > 0:
    print(f"Countdown: {count}")
    count -= 1
else:
    # This runs once count reaches 0
    print("Liftoff! The loop condition is now False.")


# =========================================
# 1.4 while Loop Where the else Clause Is Skipped
# =========================================
"""
As with the for loop, a break prevents the else clause from running.
"""

# 4. while loop example with a break
count = 5
while count > 0:
    if count == 2:
        print("Stopping at 2.")
        break
    print(f"Count: {count}")
    count -= 1
else:
    print("This will NOT print.")
