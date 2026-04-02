"""
Dictionaries are one of the fundamental data structures in Python. They’re used everywhere in the language and have gotten quite optimized over time.
"""

# Merging dictionaries
# ====================
# There are several ways you can merge two dictionaries. However, the syntax is either a bit cryptic or cumbersome:
pycon = {2016: "Portland", 2018: "Cleveland"}
europython = {2017: "Rimini", 2018: "Edinburgh", 2019: "Basel"}
{**pycon, **europython}

merged = pycon.copy()
for key, value in europython.items():
    merged[key] = value

merged


# Based on PEP 584, the new version of Python introduces two new operators for dictionaries:
# union (|) and in-place union (|=). You can use | to merge two dictionaries, while |= will update a dictionary in place:

# merge two dictionaries
pycon = {2016: "Portland", 2018: "Cleveland"}
europython = {2017: "Rimini", 2018: "Edinburgh", 2019: "Basel"}
pycon | europython

# update a dictionary in place
pycon |= europython

