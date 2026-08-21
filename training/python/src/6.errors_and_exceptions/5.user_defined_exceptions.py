# =========================================
# 1. User-Defined Exceptions
# =========================================
"""
Python allows you to create your own exceptions.

This is useful when:
- Built-in exceptions are not specific enough
- You want clearer, domain-specific error handling
- You are building larger systems or libraries
"""


# =========================================
# 1.1 Creating a Basic Custom Exception
# =========================================
"""
Custom exceptions are created by defining a class.

They should inherit from Exception.
"""

class MyError(Exception):
    pass


# Raising the custom exception
# raise MyError("Something went wrong")


# =========================================
# 1.2 Why Inherit from Exception?
# =========================================
"""
Custom exceptions should inherit from Exception (or its subclasses).

This ensures they:
- Integrate with Python's error handling system
- Are treated as non-fatal exceptions

Note:
Exceptions that do not inherit from Exception are rarely used.
"""


# =========================================
# 1.3 Adding Information to Exceptions
# =========================================
"""
Custom exceptions can store extra information.

This helps provide more detail about what went wrong.
"""

class InputError(Exception):
    def __init__(self, value, message):
        self.value = value
        self.message = message


try:
    raise InputError("abc", "Invalid number")
except InputError as e:
    print("Value:", e.value)
    print("Message:", e.message)


# =========================================
# 1.4 Using Exception Arguments
# =========================================
"""
Alternatively, use the default Exception behaviour
to store arguments in .args.
"""

class SimpleError(Exception):
    pass

try:
    raise SimpleError("spam", "eggs")
except SimpleError as e:
    print(e.args)  # ('spam', 'eggs')


# =========================================
# 1.5 Customising String Representation
# =========================================
"""
You can control how the exception is displayed by overriding __str__().
"""

class DetailedError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return f"[Error {self.code}] {self.message}"


try:
    raise DetailedError(404, "Not Found")
except DetailedError as e:
    print(e)  # Outputs: [Error 404] Not Found


# =========================================
# 1.6 Naming Conventions
# =========================================
"""
Custom exception names typically:

- End with 'Error'
- Describe the problem clearly

Examples:
- ValidationError
- DatabaseError
- ConnectionError (built-in example)
"""


# =========================================
# 1.7 Using Custom Exceptions in Practice
# =========================================
"""
Custom exceptions are useful for enforcing rules in your code.
"""

class BalanceError(Exception):
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise BalanceError("Insufficient funds")
    return balance - amount


try:
    withdraw(100, 150)
except BalanceError as e:
    print("Transaction failed:", e)


# =========================================
# 1.8 Exceptions in Modules and Libraries
# =========================================
"""
Many standard Python modules define their own exceptions.

This allows:
- Clear error types for specific problems
- More precise exception handling
"""


# =========================================
# 1.9 Key Idea
# =========================================
"""
User-defined exceptions allow you to:

- Create meaningful error types
- Improve readability and debugging
- Build structured error handling systems

They behave like any other class, but are used for signalling errors.
"""


# =========================================
# 1.10 Summary
# =========================================
"""
Creating custom exceptions involves:

- Defining a class inheriting from Exception
- Optionally storing additional data
- Optionally customising output

Key practices:
- Use clear, descriptive names
- Keep exceptions simple
- Use them when built-in types are not sufficient

Core idea:
"Define errors that match your problem domain"
"""