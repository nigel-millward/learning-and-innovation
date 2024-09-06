# In Python 3.8, some new features have been added to typing to allow more precise typing:
#  -Literal types
# - Typed dictionaries
# - Final objects
# - Protocols

# 1. Literal types
# ==================
#  Literal is a bit special in that it represents one or several specific values. One use case of Literal is to be able
#  to precisely add types, when string arguments are used to describe specific behavior.

def draw_line(direction: str) -> None:
    if direction == "horizontal":
        ...  # Draw horizontal line

    elif direction == "vertical":
        ...  # Draw vertical line

    else:
        raise ValueError(f"invalid direction {direction!r}")


draw_line("up")

# The program will pass the static type checker, even though "up" is an invalid direction.
# The type checker only checks that "up" is a string.
# In this case, it would be more precise to say that direction must be either the literal string "horizontal"
# or the literal string "vertical"
# By exposing the allowed values of direction to the type checker, you can now be warned about the error:

from typing import Literal, Dict, Any


def draw_line(direction: Literal["horizontal", "vertical"]) -> None:
    if direction == "horizontal":
        ...  # Draw horizontal line

    elif direction == "vertical":
        ...  # Draw vertical line

    else:
        raise ValueError(f"invalid direction {direction!r}")

draw_line("up")

# 2. Typed Dict
# =============
# This can be used to specify types for keys and values in a dictionary
# using a notation that is similar to the typed NamedTuple.

# Traditionally, dictionaries have been annotated using Dict. The issue is that this only allowed one type for the keys
# and one type for the values, often leading to annotations like Dict[str, Any].
# As an example, consider a dictionary that registers information about Python versions:
def count_words(text: str) -> Dict[str, Any]:
    return {"version": "3.8", "release_year": 2019}

# 3.8 with TypedDict, you can do the following:
from typing import TypedDict

class PythonVersion(TypedDict):
    version: str
    release_year: int

py38 = PythonVersion(version="3.8", release_year=2019)


# 3. Final objects
# ================
#  PEP 591 introduces Final. This qualifier specifies that a variable or attribute should not be
#  reassigned, redefined, or overridden. The following is a typing error:

from typing import Final

ID: Final = 1
ID += 1

# Additionally, there is also a @final decorator that can be applied to classes and methods.
# Classes decorated with @final can’t be subclassed, while @final methods can’t be overridden by subclasses:
from typing import final


"""
@final
class Base:
    # insert code here

class Sub(Base):
    # insert code here
"""


# 4. Protocols
# ==============
# Protocols are a way of formalizing Python’s support for duck typing:
# When I see a bird that walks like a duck and swims like a duck and quacks like a duck, I call that bird a duck.


"""
    class Duck:
        def swim(self):
            print("The duck is swimming")

        def fly(self):
            print("The duck is flying")

    class Swan:
        def swim(self):
            print("The swan is swimming")

        def fly(self):
            print("The swan is flying")

    class Albatross:
        def swim(self):
            print("The albatross is swimming")

        def fly(self):
            print("The albatross is flying")

from birds_v1 import Duck, Swan, Albatross

birds = [Duck(), Swan(), Albatross()]

for bird in birds:
   bird.fly()
   bird.swim()

# The duck is flying
# The duck is swimming
# The swan is flying
# The swan is swimming
# The albatross is flying
# The albatross is swimming`
"""


# Protocols support the duck typing.

from typing import Protocol

class Named(Protocol):
    name: str

def greet(obj: Named) -> None:
    print(f"Hi {obj.name}")