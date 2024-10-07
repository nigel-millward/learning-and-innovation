# NICER SYNTAX FOR ASYNC TASKS
# =============================

# Support for asynchronous programming in Python has evolved over a long time. Foundations were laid in the Python 2
# era with the addition of generators. The asyncio library was originally added in Python 3.4, and the async and
# await keywords followed suit in Python 3.5.
#
# The development has continued in later releases, with many small improvements added to Python’s asynchronous
# capabilities. In Python 3.11, you can use task groups, which provide a cleaner syntax for running and
# monitoring asynchronous tasks.


# 1. TRADITIONAL ASYNC TASKS WITH ASYNCIO
# ------------------------------------------
# The traditional way to run several asynchronous tasks with asyncio has been to create the tasks with create_task()
# and then await them with gather(). This gets the tasks done, but it’s a bit cumbersome to work with.

# When you organize your asyncronous tasks with gather(), part of your code will typically look like this:
import asyncio
import time
#
#
# async def write():
#     print('Hey')
#     await asyncio.sleep(1)
#     print('there')
#
#
# async def main():
#     await asyncio.gather(write(), write(), write())
#
#
# if __name__ == '__main__':
#     start = time.perf_counter()
#     asyncio.run(main())
#     elapsed = time.perf_counter() - start
#     print(f"File executed in {elapsed:0.2f} seconds")

# We created two async functions -
# First is the write() function that prints Hey then wait for 1 second and then again prints there.
# Second is main() function that executes write() function 3 times using asyncio.gather().
# And then we wrote a code that calculates the time taken to execute the async functions.

"""
Hey
Hey
Hey
there
there
there
File executed in 1.00 seconds
"""


def write_sync():
    print("Hey")
    time.sleep(1)
    print("there")


def main_sync():
    for _ in range(3):
        write_sync()


if __name__ == "__main__":
    start = time.perf_counter()
    main_sync()
    elapsed = time.perf_counter() - start
    print(f"File executed in {elapsed:0.2f} seconds")

"""
Hey
there
Hey
there
Hey
there
File executed in 3.01 seconds
"""
