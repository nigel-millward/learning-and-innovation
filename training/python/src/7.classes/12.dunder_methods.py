# =========================================
# 1. Dunder (Magic) Methods
# =========================================
"""
Dunder methods are special methods with double underscores on both sides.

They allow your objects to integrate with Python's built-in behaviour:
- Operators (+, ==, <)
- Built-in functions (len, str, repr)
- Iteration and containment checks

This module covers:
- __str__ and __repr__  (string representation)
- __eq__ and __lt__     (equality and comparison)
- __len__               (length)
- __add__               (operator overloading)
- __contains__          (membership testing)
"""


# =========================================
# 1.1 __str__ and __repr__
# =========================================
"""
__str__  — human-readable output, used by print() and str()
__repr__ — developer-facing output, used in the REPL and repr()

If only __repr__ is defined, print() falls back to it.
"""

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"  # Unambiguous — shows how to recreate

    def __str__(self):
        return f"({self.x}, {self.y})"       # Readable — for end users


p = Point(3, 4)
print(str(p))   # (3, 4)       — calls __str__
print(repr(p))  # Point(3, 4)  — calls __repr__


# =========================================
# 1.2 __eq__ — Equality
# =========================================
"""
By default, == checks identity (same object in memory).

Override __eq__ to compare by value instead.
"""

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __eq__(self, other):
        return self.celsius == other.celsius


t1 = Temperature(100)
t2 = Temperature(100)
t3 = Temperature(50)

print(t1 == t2)  # True  — same value
print(t1 == t3)  # False — different value


# =========================================
# 1.3 __lt__ — Less Than (Comparison)
# =========================================
"""
Override __lt__ to support the < operator.

Defining __lt__ also enables sorting with sorted() or list.sort().
"""

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __lt__(self, other):
        return self.celsius < other.celsius

    def __repr__(self):
        return f"Temperature({self.celsius})"


temps = [Temperature(100), Temperature(20), Temperature(55)]
print(sorted(temps))  # [Temperature(20), Temperature(55), Temperature(100)]


# =========================================
# 1.4 __len__ — Length
# =========================================
"""
Override __len__ to support len() on your objects.
"""

class Basket:
    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)


basket = Basket(["apple", "banana", "cherry"])
print(len(basket))  # 3


# =========================================
# 1.5 __add__ — Operator Overloading
# =========================================
"""
Override __add__ to define what + does between two objects.
"""

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"


v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)  # Vector(4, 6)


# =========================================
# 1.6 __contains__ — Membership Testing
# =========================================
"""
Override __contains__ to support the 'in' operator.
"""

class Playlist:
    def __init__(self, tracks):
        self.tracks = tracks

    def __contains__(self, track):
        return track in self.tracks


playlist = Playlist(["Bohemian Rhapsody", "Stairway to Heaven", "Hotel California"])
print("Stairway to Heaven" in playlist)  # True
print("Wonderwall" in playlist)           # False


# =========================================
# 1.7 Dunder Methods in Custom Exceptions
# =========================================
"""
__str__ is also commonly used in custom exceptions
to control how the error message is displayed.
"""

class ApiError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"[HTTP {self.status_code}] {self.message}"


try:
    raise ApiError(404, "Resource not found")
except ApiError as e:
    print(e)  # [HTTP 404] Resource not found


# =========================================
# 1.8 Key Idea
# =========================================
"""
Dunder methods allow your classes to:

- Behave like built-in Python types
- Support operators and built-in functions
- Integrate naturally with Python's data model

You only define the ones you need.
"""


# =========================================
# 1.9 Summary
# =========================================
"""
Common dunder methods:

- __init__      constructor
- __str__       human-readable string (print, str)
- __repr__      developer string (repr, REPL)
- __eq__        equality (==)
- __lt__        less than (<), enables sorting
- __len__       length (len)
- __add__       addition (+)
- __contains__  membership (in)

Key practices:
- Define __repr__ first — it doubles as __str__ fallback
- Keep dunder methods focused and side-effect free
- Only override what your class actually needs

Core idea:
"Make your objects feel like first-class Python citizens"
"""
