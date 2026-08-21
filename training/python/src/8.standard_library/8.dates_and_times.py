# =========================================
# 1. Dates and Times (datetime)
# =========================================
"""
The datetime module provides classes for working with dates and times.

It allows you to:
- Create and manipulate dates
- Perform calculations with time
- Format dates for output

It supports both simple and advanced use cases, including timezones.
"""


# =========================================
# 1.1 Importing the Module
# =========================================
"""
The module is commonly imported using an alias.
"""

import datetime as dt


# =========================================
# 1.2 Creating Dates
# =========================================
"""
You can create date objects directly or use built-in methods.
"""

# Current date
now = dt.date.today()

print(now)
# Example: datetime.date(2003, 12, 2)


# Creating a specific date
birthday = dt.date(1964, 7, 31)

print(birthday)
# Outputs: datetime.date(1964, 7, 31)


# =========================================
# 1.3 Formatting Dates (strftime)
# =========================================
"""
strftime() converts dates to formatted strings.

You control the format using special codes.
"""

formatted = now.strftime(
    "%m-%d-%y. %d %b %Y is a %A on the %d day of %B."
)

print(formatted)
# Example:
# 12-02-03. 02 Dec 2003 is a Tuesday on the 02 day of December.


"""
Common format codes:

- %Y → full year (2026)
- %m → month number (01–12)
- %d → day of month
- %A → weekday name
- %B → full month name
- %b → short month name
"""


# =========================================
# 1.4 Date Arithmetic
# =========================================
"""
You can subtract dates to calculate durations.

The result is a timedelta object.
"""

birthday = dt.date(1964, 7, 31)

age = now - birthday

print(age)
print(age.days)   # Number of days


# Example output:
# 14368 days, 0:00:00
# 14368


"""
This allows you to:
- Calculate age
- Measure durations
- Compare dates
"""


# =========================================
# 1.5 datetime vs date
# =========================================
"""
The datetime module provides different types:

- date → only date (year, month, day)
- datetime → date + time (hour, minute, second)
"""

current_time = dt.datetime.now()

print(current_time)
# Example: 2026-06-11 08:15:00


# =========================================
# 1.6 Timezone Awareness
# =========================================
"""
datetime objects can include timezone information.

This is useful when working with:
- global applications
- APIs
- scheduling systems
"""

# Basic example (naive datetime)
print(dt.datetime.now())

# Advanced timezone handling requires additional configuration


# =========================================
# 1.7 Common Use Cases
# =========================================
"""
The datetime module is used for:

- Logging timestamps
- Scheduling events
- Age and duration calculations
- Formatting dates for output
"""


# =========================================
# 1.8 Key Idea
# =========================================
"""
The datetime module allows you to:

- Represent dates and times
- Perform calculations with them
- Convert them into readable formats

It combines data handling with presentation.
"""


# =========================================
# 1.9 Summary
# =========================================
"""
Core tools:

- dt.date.today() → current date
- dt.date(...) → create date
- strftime() → format output
- timedelta → represent differences
- dt.datetime.now() → current date and time

Best practices:
- Use date for simple cases
- Use datetime for time-aware operations
- Use strftime() for display formatting

Core idea:
"Work with time as structured data, not just strings"
"""
