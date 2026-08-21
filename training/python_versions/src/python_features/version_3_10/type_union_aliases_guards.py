# 1.Union

#3.9
#The annotation List[Union[float, int]] means that numbers should be a list where each element is either
# a floating-point number or an integer. This works well, but the notation is a bit verbose.
# Also, you need to import both List and Union from typing.
from typing import List, Union

def mean(numbers: List[Union[float, int]]) -> float:
    return sum(numbers) / len(numbers)

#3.10
# you can replace Union[float, int] with the more succinct float | int.
# Combine this with the ability to use list instead of typing.List in type hints, which Python 3.9 introduced.
# You can then simplify your code while keeping all the type information
def mean(numbers: list[float | int]) -> float:
    return sum(numbers) / len(numbers)