"""
Function annotations were introduced in Python 3.0. The syntax supports adding arbitrary metadata to Python functions.
"""


def speed(distance: "feet", time: "seconds") -> "miles per hour":
    """Calculate speed as distance over time"""
    fps2mph = 3600 / 5280  # Feet per second to miles per hour
    return distance / time * fps2mph

# In this example, the annotations are used only as documentation for the reader.
# You’ll see later how to access annotations at runtime.
#
# PEP 484 suggested that annotations should be used for type hints.
# As type hints have grown in popularity, they’ve mostly crowded out any other uses of annotations in Python.
#
# Since there are several use cases for annotations outside of static typing, PEP 593 introduces typing.
# Annotated, which you can use to combine type hints with other information.
# You can redo the calculator.py example from above like this:

from typing import Annotated

def speed(
    distance: Annotated[float, "feet"], time: Annotated[float, "seconds"]
) -> Annotated[float, "miles per hour"]:
    """Calculate speed as distance over time"""
    fps2mph = 3600 / 5280  # Feet per second to miles per hour
    return distance / time * fps2mph


# Using Annotated could result in quite verbose code.
# One way to keep your code short and readable is to use type aliases.
# You can define new variables representing annotated types:
from typing import Annotated

Feet = Annotated[float, "feet"]
Seconds = Annotated[float, "seconds"]
MilesPerHour = Annotated[float, "miles per hour"]

def speed(distance: Feet, time: Seconds) -> MilesPerHour:
    """Calculate speed as distance over time"""
    fps2mph = 3600 / 5280  # Feet per second to miles per hour
    return distance / time * fps2mph
